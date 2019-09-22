from django_filters import rest_framework as filters, DateFilter, MultipleChoiceFilter

from apps.voucher.models import SalesDiscount, PurchaseDiscount, DebitNote, DISCOUNT_TYPES
from .models import SalesVoucher, PurchaseVoucher, STATUSES, CREDIT_NOTE_STATUSES, CreditNote


class DateFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')


class SalesVoucherFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = SalesVoucher
        fields = ()


class PurchaseVoucherFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = PurchaseVoucher
        fields = ()


class CreditNoteFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=CREDIT_NOTE_STATUSES)

    class Meta:
        model = CreditNote
        fields = ()


class DebitNoteFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=CREDIT_NOTE_STATUSES)

    class Meta:
        model = DebitNote
        fields = ()


class SalesDiscountFilterSet(filters.FilterSet):
    type = MultipleChoiceFilter(choices=DISCOUNT_TYPES)

    class Meta:
        model = SalesDiscount
        exclude = ()


class PurchaseDiscountFilterSet(filters.FilterSet):
    type = MultipleChoiceFilter(choices=DISCOUNT_TYPES)

    class Meta:
        model = PurchaseDiscount
        exclude = ()
