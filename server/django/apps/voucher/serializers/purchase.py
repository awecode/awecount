from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.serializers import StatusReversionMixin
from ..models import PurchaseDiscount, PurchaseVoucherRow, PurchaseVoucher
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin


class PurchaseDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ('company',)


class PurchaseVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')


class PurchaseVoucherCreateSerializer(StatusReversionMixin, DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin,
                                      serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = PurchaseVoucherRowSerializer(many=True)

    # def assign_voucher_number(self, validated_data, instance):
    #     if instance and instance.voucher_no:
    #         return
    #     if validated_data.get('status') in ['Draft', 'Cancelled']:
    #         return
    #     next_voucher_no = get_next_voucher_no(PurchaseVoucher, self.context['request'].company_id)
    #     validated_data['voucher_no'] = next_voucher_no

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
        # self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        voucher = PurchaseVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.create(voucher=voucher, **row)
        PurchaseVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        self.assign_fiscal_year(validated_data, instance=instance)
        # self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        PurchaseVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        PurchaseVoucher.apply_transactions(instance)
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
        fields = ('id', 'voucher_no', 'party', 'date', 'name',)


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
    bank_account_name = serializers.ReadOnlyField(source='bank_account.__str__()')
    discount_obj = PurchaseDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')

    rows = PurchaseVoucherRowDetailSerializer(many=True)
    tax_registration_number = serializers.ReadOnlyField(source='party.tax_registration_number')

    class Meta:
        model = PurchaseVoucher
        exclude = ('company', 'user', 'bank_account',)
