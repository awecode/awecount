from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import PurchaseDiscount, PurchaseVoucherRow, PurchaseVoucher
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin


class PurchaseDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ('company',)


class PurchaseVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    unit_id = serializers.IntegerField(source='unit.id', required=False)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')


class PurchaseVoucherCreateSerializer(DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin,
                                      serializers.ModelSerializer):
    rows = PurchaseVoucherRowSerializer(many=True)

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        voucher = PurchaseVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            PurchaseVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        PurchaseVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        PurchaseVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            PurchaseVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        PurchaseVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ('company', 'user', 'bank_account', 'discount_obj',)


class PurchaseVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}'.format(obj.voucher_no)

    class Meta:
        model = PurchaseVoucher
        fields = ('id', 'voucher_no', 'party', 'date', 'name',)
