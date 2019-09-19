from django_filters import rest_framework as filters, DateFilter, MultipleChoiceFilter

from .models import SalesVoucher, PurchaseVoucher, STATUSES


class SalesVoucherFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = SalesVoucher
        fields = ()


class PurchaseVoucherFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = PurchaseVoucher
        fields = ()
