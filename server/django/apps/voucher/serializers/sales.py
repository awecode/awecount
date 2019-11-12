import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.product.models import Item
from apps.tax.serializers import TaxSchemeSerializer
from apps.voucher.models import SalesAgent
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin
from awecount.utils import get_next_voucher_no
from awecount.utils.serializers import StatusReversionMixin
from ..models import SalesVoucherRow, SalesVoucher, InvoiceDesign, SalesDiscount, CreditNote, PurchaseVoucher


class SalesDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDiscount
        exclude = ('company',)


class SalesDiscountMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDiscount
        fields = ('id', 'name', 'type', 'value')


class SalesVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')


class SalesVoucherRowAccessSerializer(SalesVoucherRowSerializer):
    item_id = serializers.IntegerField(required=False)
    item_obj = serializers.DictField(required=False)
    item_code = serializers.ReadOnlyField(source='item.code')

    def validate(self, data):
        data = super().validate(data)
        if 'item_id' not in data:
            if 'item_obj' not in data:
                raise ValidationError({'item': ['item_id or item_obj is required.']})
            if 'code' not in data['item_obj']:
                raise ValidationError({'item': ['item_obj.code is required.']})
            try:
                item_obj = Item.objects.get(code=data['item_obj'].get('code'), company_id=self.context['request'].company_id)
                # if data['item_obj'].get('name') and item_obj.name != data['item_obj'].get('name'):
                #     item_obj.name = data['item_obj'].get('name')
                #     item_obj.save()
            except Item.DoesNotExist:
                item_obj = Item.objects.create(code=str(data['item_obj'].get('code')),
                                               name=str(data['item_obj'].get('name') or data['item_obj'].get('code')),
                                               unit_id=data['unit_id'],
                                               category_id=data.get('category_id'),
                                               selling_price=data['rate'], tax_scheme_id=data['tax_scheme_id'],
                                               company_id=self.context['request'].company_id)
            data['item_id'] = item_obj.id
            del data['item_obj']

        return data


class SalesVoucherCreateSerializer(StatusReversionMixin, DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin,
                                   serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    print_count = serializers.ReadOnlyField()
    rows = SalesVoucherRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get('status') in ['Draft', 'Cancelled']:
            return
        next_voucher_no = get_next_voucher_no(SalesVoucher, self.context['request'].company_id)
        validated_data['voucher_no'] = next_voucher_no

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context['request'].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get('date')):
            validated_data['fiscal_year_id'] = fiscal_year.id
        else:
            raise ValidationError(
                {'date': ['Date not in current fiscal year.']},
            )

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        instance = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            SalesVoucherRow.objects.create(voucher=instance, **row)
        instance.apply_transactions()
        instance.synchronize()
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        self.assign_fiscal_year(validated_data, instance=instance)
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            SalesVoucherRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        instance.apply_transactions()
        # instance.synchronize(verb='PATCH')
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user', 'bank_account', 'discount_obj', 'fiscal_year',)


class SalesVoucherAccessSerializer(SalesVoucherCreateSerializer):
    '''
    {"mode":"Cash","customer_name":"","status":"Issued","address":"ASD","discount_type":null,"discount":0,"is_export":false,"date":"2019-11-07","due_date":"2019-11-07","rows":[{"quantity":1,"discount":0,"discount_type":null,"trade_discount":false,"item_id":401,"tax_scheme_id":45,"rate":500,"unit_id":25,"description":""}],"trade_discount":true}

    '''

    date = serializers.DateField(default=datetime.datetime.today().date)
    rows = SalesVoucherRowAccessSerializer(many=True)
    pdf_url = serializers.ReadOnlyField()
    view_url = serializers.ReadOnlyField()


class SalesVoucherRowDetailSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField()
    item_name = serializers.ReadOnlyField(source='item.name')
    unit_name = serializers.ReadOnlyField(source='unit.name')
    discount_obj = SalesDiscountSerializer()
    tax_scheme = TaxSchemeSerializer()

    class Meta:
        model = SalesVoucherRow
        exclude = ('voucher', 'item', 'unit')


class SalesVoucherDetailSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')
    bank_account_name = serializers.ReadOnlyField(source='bank_account.friendly_name')
    discount_obj = SalesDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')

    rows = SalesVoucherRowDetailSerializer(many=True)
    tax_registration_number = serializers.ReadOnlyField(source='party.tax_registration_number')
    enable_row_description = serializers.ReadOnlyField(source='company.sales_setting.enable_row_description')

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user', 'bank_account',)


class SalesVoucherListSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = SalesVoucher
        fields = ('id', 'voucher_no', 'party_name', 'date', 'status', 'customer_name', 'total_amount')


class SaleVoucherOptionsSerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField(source='pk')
    text = serializers.ReadOnlyField(source='voucher_no')

    class Meta:
        model = SalesVoucher
        fields = ('value', 'text',)


class InvoiceDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDesign
        exclude = ('company',)


class SalesBookSerializer(serializers.ModelSerializer):
    buyers_name = serializers.ReadOnlyField(source='buyer_name')
    buyers_pan = serializers.ReadOnlyField(source='party.tax_registration_number')
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')

    class Meta:
        model = SalesVoucher
        fields = ('id', 'date', 'buyers_name', 'buyers_pan', 'voucher_no', 'voucher_meta', 'is_export')


class PurchaseBookSerializer(serializers.ModelSerializer):
    sellers_name = serializers.ReadOnlyField(source='party.name')
    sellers_pan = serializers.ReadOnlyField(source='party.tax_registration_number')
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')

    class Meta:
        model = PurchaseVoucher
        fields = ('id', 'date', 'sellers_name', 'sellers_pan', 'voucher_no', 'voucher_meta', 'is_import',)


class SalesAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAgent
        exclude = ('company',)


class SalesRowSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.name")
    # unit  = serializers.CharField(source="unit.name")
    buyers_name = serializers.ReadOnlyField(source='voucher.buyer_name')
    buyers_pan = serializers.ReadOnlyField(source='voucher.party.tax_registration_number')
    bill_no = serializers.CharField(source="voucher.voucher_no")
    date = serializers.CharField(source="voucher.date")
    # voucher_id = serializers.CharField(source="voucher.id")
    tax_scheme = serializers.CharField(source="tax_scheme.name")
    amount = serializers.CharField(source='total_amount')
    row_discount = serializers.SerializerMethodField()
    voucher_discount = serializers.SerializerMethodField()
    # tax_amount = serializers.SerializerMethodField()
    tax_rate = serializers.ReadOnlyField(source='tax_scheme.rate')

    # def get_tax_amount(self, obj):
    #     return obj.tax_scheme.rate * obj.rate / 100

    def get_row_discount(self, obj):
        return obj.get_discount()

    def get_voucher_discount(self, obj):
        return obj.voucher.get_discount(use_prefetched=True)

    class Meta:
        model = SalesVoucherRow
        fields = (
            'id', 'item', 'buyers_name', 'buyers_pan', 'bill_no', 'voucher_id', 'tax_scheme', 'rate', 'quantity', 'date',
            'amount', 'tax_rate',
            'row_discount', 'voucher_discount')
