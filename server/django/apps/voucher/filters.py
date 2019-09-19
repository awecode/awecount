from django_filters import rest_framework as filters, DateFilter, MultipleChoiceFilter

from apps.voucher.models import SalesDiscount, PurchaseDiscount
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


class SalesDiscountFilterSet(filters.FilterSet):
    class Meta:
        model = SalesDiscount
        exclude = ()


class PurchaseDiscountFilterSet(filters.FilterSet):
    class Meta:
        model = PurchaseDiscount
        exclude = ()
