import datetime

from django.core.exceptions import ValidationError
from django.db.models import F, Q
from rest_framework import serializers

from apps.product.models import Item, Transaction
from apps.voucher.models import (
    InventoryConversionVoucher,
    InventoryConversionVoucherRow,
)
from awecount.libs import get_next_voucher_no
from awecount.libs.exception import UnprocessableException


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
                {"rate": "Rate is required for debit transaction."}
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
            InventoryConversionVoucher, self.context["request"].company_id
        )
        validated_data["voucher_no"] = next_voucher_no

    def validate(self, data):
        request = self.context["request"]
        bill_of_material = data.get("finished_product", None)
        if bill_of_material is not None:
            finished_product = bill_of_material.finished_product

        dr_item_ids = []
        cr_item_ids = []

        for row in data["rows"]:
            if row.get("transaction_type") == "Dr":
                dr_item_ids.append(row["item_id"])
            else:
                cr_item_ids.append(row["item_id"])

        if (not cr_item_ids) or (not dr_item_ids):
            raise ValidationError({"detail": "Dr and Cr items are required"})

        if finished_product is not None:
            for item_id in dr_item_ids:
                if item_id != finished_product.id:
                    dr_item_ids.append(finished_product.id)

        for row in data["rows"]:
            if row["item_id"] in cr_item_ids and row["item_id"] in dr_item_ids:
                raise ValidationError(
                    {"detail": "Same item cannot be in both Dr and Cr"}
                )

        quantities = {
            row["item_id"]: row["quantity"]
            for row in data["rows"]
            if row.get("transaction_type") == "Cr"
        }

        # Check negative stock
        inventory_setting = request.company.inventory_setting
        if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
            items = (
                Item.objects.filter(id__in=cr_item_ids)
                .annotate(remaining=F("account__current_balance"))
                .only("id")
            )

            remaining_stock_map = {item.id: item.remaining for item in items}

            for item in items:
                if remaining_stock_map[item.id] < quantities[item.id]:
                    raise UnprocessableException(
                        detail=f"You do not have enough stock for item {item.name} in your inventory to create this sales. Available stock: {item.remaining} {item.unit.name if item.unit else 'units'}",
                        code="negative_stock",
                    )

        if inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            item_ids = [row["item_id"] for row in data["rows"]]
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")
            items_transactions = Transaction.objects.filter(
                Q(account__item__id__in=item_ids) & Q(journal_entry__date__gt=date)
            )
            if items_transactions.exists():
                raise UnprocessableException(
                    detail="There are Transactions on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",
                )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_voucher_number(validated_data, instance=None)
        instance = InventoryConversionVoucher.objects.create(**validated_data)
        for row in rows_data:
            if row.get("id"):
                row.pop("id")
            InventoryConversionVoucherRow.objects.create(voucher=instance, **row)
        instance.apply_inventory_transactions()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # prevent form updating finished_product
        validated_data.pop("finished_product", None)
        rows_data = validated_data.pop("rows")
        InventoryConversionVoucher.objects.filter(pk=instance.id).update(
            **validated_data
        )
        for row in rows_data:
            InventoryConversionVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
            instance.apply_inventory_transactions()
            instance.save()
        return instance

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryConversionVoucher
        fields = [
            "id",
            "voucher_no",
            "date",
            "status",
        ]


class InventoryConversionVoucherDetailSerializer(serializers.ModelSerializer):
    rows = InventoryConversionVoucherRowSerializer(many=True)
    finished_product_name = serializers.ReadOnlyField(
        source="finished_product.finished_product.name"
    )

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionFinishedProductList(serializers.Serializer):
    name = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ("id", "name")
