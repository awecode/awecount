from rest_framework import serializers

from .models import SalesVoucherRow, SalesVoucher


class SalesVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme = serializers.IntegerField(source='tax_scheme.id', required=True)
    purchase_order = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme',)


class SalesVoucherCreateSerializer(serializers.ModelSerializer):
    rows = SalesVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        voucher = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            tax_schema = row.pop('item')
            row['tax_schema_id'] = tax_schema
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            row['tax_scheme_id'] = item.get('tax_scheme')
            SalesVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company',)


class SalesVoucherListSerializer(serializers.ModelSerializer):


    class Meta:
        model = SalesVoucher
        fields = ('voucher_no', 'party', 'transaction_date',)
