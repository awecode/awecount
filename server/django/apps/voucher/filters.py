from django_filters import rest_framework as filters, DateFilter

from .models import SalesVoucher


class SalesVoucherDateFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='transaction_date', lookup_expr='gte', )
    end_date = DateFilter(field_name='transaction_date', lookup_expr='lte')

    class Meta:
        model = SalesVoucher
        fields = ()
