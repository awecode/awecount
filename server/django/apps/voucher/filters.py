from django_filters import rest_framework as filters, DateFilter

from .models import SalesVoucher, PurchaseVoucher


class SalesVoucherDateFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = SalesVoucher
        fields = ()


class PurchaseVoucherDateFilterSet(filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', )
    end_date = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = PurchaseVoucher
        fields = ()
