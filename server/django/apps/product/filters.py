from django_filters import rest_framework as filters

from apps.voucher.filters import DateFilterSet

from .models import (
    ADJUSTMENT_STATUS_CHOICES,
    CONVERSION_CHOICES,
    InventoryAccount,
    InventoryAdjustmentVoucher,
    InventoryConversionVoucher,
    Item,
)


class ItemFilterSet(filters.FilterSet):
    class Meta:
        model = Item
        fields = ("can_be_sold", "can_be_purchased", "search_data", "category")


class InventoryAccountFilterSet(filters.FilterSet):
    class Meta:
        model = InventoryAccount
        fields = ("opening_balance",)


class BookFilterSet(filters.FilterSet):
    language = filters.CharFilter(field_name="extra_data__language")
    genre = filters.CharFilter(field_name="extra_data__genre")
    format = filters.CharFilter(field_name="extra_data__format")

    class Meta:
        model = Item
        fields = (
            "can_be_sold",
            "can_be_purchased",
            "search_data",
            "brand",
        )


class InventoryAdjustmentVoucherFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=ADJUSTMENT_STATUS_CHOICES)

    class Meta:
        model = InventoryAdjustmentVoucher
        fields = []


class InventoryConversionVoucherFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=CONVERSION_CHOICES)

    class Meta:
        model = InventoryConversionVoucher
        fields = []
