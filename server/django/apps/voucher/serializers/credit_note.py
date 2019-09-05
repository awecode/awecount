from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ..models import CreditVoucherRow, CreditVoucher
from .sales import SaleVoucherOptionsSerializer


class CreditVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    receipt = serializers.FloatField(required=False)
    # invoice_id = serializers.IntegerField(source='invoice.id', required=True)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    cash_receipt_id = serializers.IntegerField(source='cash_receipt.id', required=False, read_only=True)

    class Meta:
        model = CreditVoucherRow
        exclude = ('item', 'tax_scheme', 'cash_receipt',)


class CreditVoucherCreateSerializer(serializers.ModelSerializer):
    rows = CreditVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()
    sale_vouchers_options = serializers.SerializerMethodField(read_only=True)
    fetched_sale_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_sale_vouchers_options(self, obj):
        sale_vouchers = obj.sale_vouchers.all()
        data = SaleVoucherOptionsSerializer(sale_vouchers, many=True).data
        return data

    def get_fetched_sale_vouchers(self, obj):
        data = [voucher.id for voucher in obj.sale_vouchers.all()]
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        sale_vouchers = validated_data.pop('sale_vouchers')
        credit_voucher = CreditVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            CreditVoucherRow.objects.create(cash_receipt=credit_voucher, **row)
        credit_voucher.sale_vouchers.add(*sale_vouchers)
        CreditVoucher.apply_transactions(credit_voucher)
        return credit_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        sale_vouchers = validated_data.pop('sale_vouchers')
        CreditVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            row['cash_receipt'] = instance
            try:
                CreditVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'non_field_errors': ['Voucher repeated in cash receipt.']})
        instance.sale_vouchers.clear()
        instance.sale_vouchers.add(*sale_vouchers)
        instance.refresh_from_db()
        CreditVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = CreditVoucher
        exclude = ('company',)


class CreditVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditVoucher
        fields = ('id', 'voucher_no', 'party', 'date',)
