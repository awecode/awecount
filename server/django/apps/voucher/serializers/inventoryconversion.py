from rest_framework import serializers

from apps.voucher.models import (
    InventoryConversionVoucher,
    InventoryConversionVoucherRow,
)
from awecount.libs import get_next_voucher_no


class InventoryConversionVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=True)
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")

    def validate(self, attrs):
        transaction_type = attrs.get("transaction_type")
        rate = attrs.get("rate", None)

        if transaction_type == "Dr" and not rate:
            raise serializers.ValidationError(
                {"detail": "Rate is required for debit transaction."}
            )

        if transaction_type == "Cr" and rate:
            raise serializers.ValidationError(
                {"detail": "Rate is not allowed for credit transaction."}
            )

        return super().validate(attrs)

    class Meta:
        model = InventoryConversionVoucherRow
        exclude = (
            "item",
            "voucher",
            "unit",
        )


class InventoryConversionVoucherCreateSerializer(serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = InventoryConversionVoucherRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            InventoryConversionVoucherRow, self.context["request"].company_id
        )
        validated_data["voucher_no"] = next_voucher_no
    
    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_voucher_number(validated_data, instance=None)
        instance = InventoryConversionVoucher.objects.create(**validated_data)
        for row in rows_data:
            if row.get("id"):
                row.pop("id") 
            InventoryConversionVoucherRow.objects.create(voucher=instance, **row)
        instance.save()
        return instance

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryConversionVoucher
        fields = ["id", "voucher_no", "date"]


class InventoryConversionVoucherDetailSerializer(serializers.ModelSerializer):
    rows = InventoryConversionVoucherRowSerializer(many=True)

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionFinishedProductList(serializers.Serializer):
    name = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ("id", "name")
