from datetime import date
from django_filters import rest_framework as filters, DateFilter, MultipleChoiceFilter

from apps.voucher.models import SalesDiscount, PurchaseDiscount, DebitNote, DISCOUNT_TYPES, JournalVoucher, \
    SalesVoucherRow
from .models import SalesVoucher, PurchaseVoucher, STATUSES, CREDIT_NOTE_STATUSES, CreditNote


class DateFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')


class SalesVoucherFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)
    is_due = filters.BooleanFilter(method='is_due_filter')

    def is_due_filter(self, queryset, name, value):
        today = date.today()
        return queryset.filter(due_date__lt=today).exclude(status="PAID")

    class Meta:
        model = SalesVoucher
        fields = ()


class SalesRowFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='voucher__date', lookup_expr='gte', )
    end_date = DateFilter(field_name='voucher__date', lookup_expr='lte')
    sales_agent = filters.CharFilter(field_name='voucher__sales_agent__name')

    class Meta:
        model = SalesVoucherRow
        fields = ('sales_agent',)


class PurchaseVoucherFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)
    is_due = filters.BooleanFilter(method='is_due_filter')

    def is_due_filter(self, queryset, name, value):
        today = date.today()
        return queryset.filter(due_date__lt=today).exclude(status="PAID")

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


class JournalVoucherFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=JournalVoucher.STATUSES)

    class Meta:
        model = JournalVoucher
        exclude = ()
