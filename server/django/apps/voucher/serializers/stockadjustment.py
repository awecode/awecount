import datetime

from django.db.models import F, Q
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from apps.ledger.serializers import JournalEntrySerializer
from apps.product.models import Item, Transaction
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
        

    def validate(self, data):
        request = self.context["request"]
        data = super().validate(data)
        inventory_setting = request.company.inventory_setting
        item_ids = {row["item_id"] for row in data["rows"]}
        if inventory_setting.enable_negative_stock_check and not request.query_params.get("negative_stock") and not data.get("purpose") == 'Stock In':
            quantities = {}
            for row in data["rows"]:
                item_id = row["item_id"]
                quantity = row["quantity"]
                if quantities.get(item_id):
                    quantities[item_id] += quantity
                else:
                    quantities[item_id] = quantity
            items = (
                Item.objects.filter(id__in=item_ids)
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
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")
            items_transactions = (
                Transaction.objects.filter(Q(account__item__id__in=item_ids) & Q(journal_entry__date__gt=date))
            )
            if items_transactions.exists():
                raise UnprocessableException(
                    detail="There are Transactions on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",)
        return data


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
    
    @action(detail=True, url_path="journal-entries")
    def journal_entries(self, request, pk):
        stock_adjustment_voucher = get_object_or_404(StockAdjustmentVoucher, pk=pk)
        journals = stock_adjustment_voucher.journal_entries()
        return Response(JournalEntrySerializer(journals, many=True).data)

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
