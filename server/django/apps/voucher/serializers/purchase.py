from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.product.models import Item

from apps.tax.serializers import TaxSchemeSerializer
from awecount.libs import get_next_voucher_no
from awecount.libs.serializers import StatusReversionMixin
from ..models import PurchaseDiscount, PurchaseOrder, PurchaseOrderRow, PurchaseVoucherRow, PurchaseVoucher
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin


class PurchaseDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ('company',)
        extra_kwargs = {
            "name": {"required": True}
        }


class PurchaseVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')

        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False}
        }


class PurchaseVoucherCreateSerializer(StatusReversionMixin, DiscountObjectTypeSerializerMixin,
                                      ModeCumBankSerializerMixin,
                                      serializers.ModelSerializer):
    rows = PurchaseVoucherRowSerializer(many=True)
    purchase_order_numbers = serializers.ReadOnlyField()

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
        
        if data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        return data

        # if request.query_params.get("fifo_inconsistency"):
        #     return data
        # else:
        #     if request.company.inventory_setting.enable_fifo:
        #         item_ids = [x.get("item_id") for x in data.get("rows")]
        #         date = data["date"]
        #         if PurchaseVoucherRow.objects.filter(voucher__date__gt=date, item__in=item_ids, item__track_inventory=True).exists():
        #             raise UnprocessableException(detail="Creating a purchase on a past date when purchase for the same item on later dates exist may cause inconsistencies in FIFO.", code="fifo_inconsistency")
        #     return data

    def validate_rows(self, rows):
        for row in rows:
            if not row.get("discount"):
                row["discount"] = 0
            if row.get("discount_type") == "":
                row["discount_type"] = None
        return rows
    
    # def validate_discount_type(self, attr):
    #     if not attr:
    #         attr = 0
    #     return attr
    
    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        purchase_orders = validated_data.pop('purchase_orders', None)
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        instance = PurchaseVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            if request.company.inventory_setting.enable_fifo:
                # TODO: use this from request data
                item = Item.objects.get(id=row["item_id"])
                if item.track_inventory:
                    row["remaining_quantity"] = row["quantity"]
            PurchaseVoucherRow.objects.create(voucher=instance, **row)
        if purchase_orders:
            instance.purchase_orders.clear()
            instance.purchase_orders.set(purchase_orders)
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        purchase_orders = validated_data.pop('purchase_orders', None)
        self.assign_fiscal_year(validated_data, instance=instance)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        PurchaseVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        if purchase_orders:
            instance.purchase_orders.clear()
            instance.purchase_orders.set(purchase_orders)
        instance.refresh_from_db()
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ('company', 'user', 'bank_account', 'discount_obj', 'fiscal_year')


class PurchaseVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}'.format(obj.voucher_no)

    class Meta:
        model = PurchaseVoucher
        fields = ('id', 'voucher_no', 'party', 'date', 'name', 'status', 'total_amount', 'mode')


class PurchaseVoucherRowDetailSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField()
    item_name = serializers.ReadOnlyField(source='item.name')
    unit_name = serializers.ReadOnlyField(source='unit.name')
    discount_obj = PurchaseDiscountSerializer()
    tax_scheme = TaxSchemeSerializer()

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('voucher', 'item', 'unit')


class PurchaseVoucherDetailSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')
    bank_account_name = serializers.ReadOnlyField(source='bank_account.friendly_name')
    discount_obj = PurchaseDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')

    rows = PurchaseVoucherRowDetailSerializer(many=True)
    tax_registration_number = serializers.ReadOnlyField(source='party.tax_registration_number')
    enable_row_description = serializers.ReadOnlyField(source='company.purchase_setting.enable_row_description')
    purchase_order_numbers = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseVoucher
        exclude = ('company', 'user', 'bank_account',)


class PurchaseBookExportSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')
    tax_registration_number = serializers.ReadOnlyField(source='party.tax_registration_number')
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')
    item_names = serializers.ReadOnlyField()
    total_quantity = serializers.SerializerMethodField()

    def get_total_quantity(self, obj):
        # Annotate this on queryset on api that uses this serializer
        return obj.total_quantity

    class Meta:
        model = PurchaseVoucher
        fields = ('date', 'party_name', 'tax_registration_number', 'voucher_no', 'voucher_meta', 'item_names', 'units',
                  'total_quantity')


class PurchaseOrderRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = PurchaseOrderRow
        exclude = ['item', 'voucher', 'unit']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'voucher_no', 'party_name', 'date', 'status']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    print_count = serializers.ReadOnlyField()
    rows = PurchaseOrderRowSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        exclude = ['company', 'user']
        extra_kwargs = {
            'fiscal_year': {'read_only': True}
        }

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context['request'].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get('date')):
            validated_data['fiscal_year_id'] = fiscal_year.id
        else:
            raise ValidationError({
                'date': ['Date not in current fiscal year.']
            })

    def assign_voucher_number(self, validated_data, instance=None):
        if instance and instance.voucher_no:
            return
        next_voucher_no = get_next_voucher_no(PurchaseOrder, self.context['request'].company_id)
        validated_data['voucher_no'] = next_voucher_no

    def validate_party(self, attr):
        if not attr:
            raise ValidationError("You must select a party.")
        return attr

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        instance = PurchaseOrder.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            PurchaseOrderRow.objects.create(voucher=instance, **row)
        return instance
    
    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        self.assign_fiscal_year(validated_data, instance=instance)
        # self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.Meta.model.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            PurchaseOrderRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        return instance