from rest_framework import serializers

from apps.voucher.models import StockAdjustmentVoucher, StockAdjustmentVoucherRow
from awecount.libs import get_next_voucher_no


class StockAdjustmentVoucherRowSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=True)

    class Meta:
        model = StockAdjustmentVoucherRow
        exclude = (
            "item",
            "voucher",
            # "unit",
        )
        
        


class StockAdjustmentVoucherRowDetailSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.name")
    unit = serializers.CharField(source="unit.name")

    class Meta:
        model = StockAdjustmentVoucherRow
        exclude = ("items", "voucher", "unit")


class StockAdjustmentVoucherCreateSerializer(serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = StockAdjustmentVoucherRowSerializer(many=True)

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
        self.assign_voucher_number(validated_data, instance=None)
        instance = StockAdjustmentVoucher.objects.create(**validated_data)
        return instance

    class Meta:
        model = StockAdjustmentVoucher
        exclude = ("company",)


class StockAdjustmentVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        exclude = ("company", "issue_datetime", "remarks")


class StockAdjustmentVoucherDetailSerializer(serializers.ModelSerializer):
    row = StockAdjustmentVoucherRowDetailSerializer(many=True)

    class Meta:
        model = StockAdjustmentVoucher
        exclude = ("company",)
