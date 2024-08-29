from datetime import date

from django_filters import rest_framework as filters

from apps.voucher.models import (
    DISCOUNT_TYPES,
    PAYMENT_MODES,
    PAYMENT_STATUSES,
    Challan,
    DebitNote,
    PaymentReceipt,
    PurchaseDiscount,
    SalesDiscount,
    SalesVoucherRow,
)
from apps.voucher.models.journal_vouchers import JournalVoucher

from .models import (
    ADJUSTMENT_STATUS_CHOICES,
    CHALLAN_STATUSES,
    CREDIT_NOTE_STATUSES,
    PURCHASE_ORDER_STATUS_CHOICES,
    STATUSES,
    CONVERSION_CHOICES,
    CreditNote,
    PurchaseOrder,
    PurchaseVoucher,
    PurchaseVoucherRow,
    SalesVoucher,
    InventoryAdjustmentVoucher,
    InventoryConversionVoucher,
)


class DateFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")


class SalesVoucherFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=STATUSES)
    is_due = filters.BooleanFilter(method="is_due_filter")

    def is_due_filter(self, queryset, name, value):
        today = date.today()
        return queryset.filter(due_date__lt=today).exclude(status="Paid")

    class Meta:
        model = SalesVoucher
        fields = ()


class SalesRowFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(field_name="voucher__date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="voucher__date", lookup_expr="lte")
    sales_agent = filters.CharFilter(field_name="voucher__sales_agent")
    status = filters.MultipleChoiceFilter(
        field_name="voucher__status", choices=STATUSES
    )
    party = filters.CharFilter(field_name="voucher__party")
    item_category = filters.CharFilter(field_name="item__category")

    class Meta:
        model = SalesVoucherRow
        fields = ("sales_agent", "tax_scheme", "item")


class PurchaseVoucherFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=STATUSES)
    is_due = filters.BooleanFilter(method="is_due_filter")

    def is_due_filter(self, queryset, name, value):
        today = date.today()
        return queryset.filter(due_date__lt=today).exclude(status="Paid")

    class Meta:
        model = PurchaseVoucher
        fields = ()

class PurchaseVoucherRowFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(field_name="voucher__date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="voucher__date", lookup_expr="lte")
    purchase_agent = filters.CharFilter(field_name="voucher__sales_agent")
    status = filters.MultipleChoiceFilter(
        field_name="voucher__status", choices=STATUSES
    )
    party = filters.CharFilter(field_name="voucher__party")
    item_category = filters.CharFilter(field_name="item__category")

    class Meta:
        model = PurchaseVoucherRow
        fields = ("purchase_agent", "tax_scheme", "item")


class CreditNoteFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=CREDIT_NOTE_STATUSES)

    class Meta:
        model = CreditNote
        fields = ()


class DebitNoteFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=CREDIT_NOTE_STATUSES)

    class Meta:
        model = DebitNote
        fields = ()


class SalesDiscountFilterSet(filters.FilterSet):
    type = filters.MultipleChoiceFilter(choices=DISCOUNT_TYPES)

    class Meta:
        model = SalesDiscount
        exclude = ()


class PurchaseDiscountFilterSet(filters.FilterSet):
    type = filters.MultipleChoiceFilter(choices=DISCOUNT_TYPES)

    class Meta:
        model = PurchaseDiscount
        exclude = ()


class JournalVoucherFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=JournalVoucher.STATUSES)

    class Meta:
        model = JournalVoucher
        exclude = ()


class PaymentReceiptFilterSet(DateFilterSet):
    party = filters.CharFilter()
    mode = filters.MultipleChoiceFilter(choices=PAYMENT_MODES)
    status = filters.MultipleChoiceFilter(choices=PAYMENT_STATUSES)
    sales_agent = filters.CharFilter(field_name="invoices__sales_agent")

    class Meta:
        model = PaymentReceipt
        fields = ()


class ChallanFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=CHALLAN_STATUSES)

    class Meta:
        model = Challan
        fields = ()


class PurchaseOrderFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=PURCHASE_ORDER_STATUS_CHOICES)

    class Meta:
        model = PurchaseOrder
        fields = []


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
