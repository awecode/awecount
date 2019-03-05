from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import SalesVoucherRow, SalesVoucher, CreditVoucherRow, CreditVoucher


class SalesVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher')


class SalesVoucherCreateSerializer(serializers.ModelSerializer):
    rows = SalesVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        user_id = request.user.id
        validated_data['user_id'] = user_id
        voucher = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            SalesVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user',)


class SalesVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}: {}'.format(obj.voucher_no, obj.user)

    class Meta:
        model = SalesVoucher
        fields = ('id', 'voucher_no', 'party', 'transaction_date', 'status', 'name',)


class CreditVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    invoice_id = serializers.IntegerField(source='invoice.id', required=True)
    cash_receipt_id = serializers.IntegerField(source='cash_receipt.id', required=False, read_only=True)

    class Meta:
        model = CreditVoucherRow
        exclude = ('invoice', 'cash_receipt', )


class CreditVoucherCreateSerializer(serializers.ModelSerializer):
    rows = CreditVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        cash_receipt = CreditVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            invoice = row.pop('invoice')
            try:
                CreditVoucherRow.objects.create(cash_receipt=cash_receipt, invoice_id=invoice.get('id'), **row)
            except IntegrityError:
                raise APIException({'errors': ['Voucher repeated in cash receipt.']})
        return cash_receipt

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        CreditVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            invoice = row.pop('invoice')
            row['cash_receipt'] = instance
            row['invoice_id'] = invoice.get('id')
            try:
                CreditVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'errors': ['Voucher repeated in cash receipt.']})
        instance.refresh_from_db()
        return instance

    class Meta:
        model = CreditVoucher
        exclude = ('company', 'receipt',)


class CreditVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditVoucher
        fields = ('id', 'voucher_no', 'party', 'date',)
