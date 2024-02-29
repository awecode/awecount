from rest_framework import serializers

from apps.product.models import InventoryAccount
from apps.voucher.models import StockAdjustmentVoucher, StockAdjustmentVoucherRow
from awecount.libs import get_next_voucher_no
from awecount.libs.exception import UnprocessableException


class StockAdjustmentVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=True)
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    
    class Meta:
        model = StockAdjustmentVoucherRow
        exclude = (
            "item",
            "voucher",
            "unit",
        )


class StockAdjustmentVoucherCreateSerializer(serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = StockAdjustmentVoucherRowSerializer(many=True)
    total_amount = serializers.ReadOnlyField()

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            StockAdjustmentVoucher, self.context["request"].company_id
        )
        validated_data["voucher_no"] = next_voucher_no
        

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_voucher_number(validated_data, instance=None)
        instance = StockAdjustmentVoucher.objects.create(**validated_data)
        total_amount = 0
        for index, row in enumerate(rows_data):
            if row.get("id"):
                row.pop("id")
            quantity = row.get('quantity')
            rate = row.get('rate')
            total_amount += (rate * quantity)
            StockAdjustmentVoucherRow.objects.create(voucher=instance, **row)
        instance.total_amount = total_amount
        instance.save()
        instance.apply_transactions()
        request = self.context["request"]
        inventory_setting = request.company.inventory_settings
        if  instance.apply_transaction.transaction_type=="cr" :
            if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
                for rows in row:
                    if InventoryAccount.current_balance<row.cr.amount:
                        raise UnprocessableException()
                    InventoryAccount.current_balance-=row.cr.amount

        return instance

    def update(self, instance, validated_data):
        # prevent form updating purpose
        validated_data.pop("purpose")
        rows_data = validated_data.pop("rows")
        total_amount = 0
        StockAdjustmentVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            StockAdjustmentVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
            quantity = row.get('quantity')
            rate = row.get('rate')
            total_amount += (rate * quantity)
        if instance.total_amount != total_amount:
            instance.total_amount = total_amount
            instance.save()
        instance.apply_transactions()
        return instance

    class Meta:
        model = StockAdjustmentVoucher
        exclude = ("company",)


class StockAdjustmentVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        fields=['id', 'voucher_no', 'date', 'status','purpose', 'total_amount']


class StockAdjustmentVoucherDetailSerializer(serializers.ModelSerializer):
    rows = StockAdjustmentVoucherRowSerializer(many=True)

    class Meta:
        model = StockAdjustmentVoucher
        exclude = ("company",)
