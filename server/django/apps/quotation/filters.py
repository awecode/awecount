from apps.quotation.models import STATUSES, Quotation
from django_filters import rest_framework as filters
from datetime import date


class DateFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")


class QuotationFilterSet(DateFilterSet):
    status = filters.MultipleChoiceFilter(choices=STATUSES)
    is_expired = filters.BooleanFilter(method="is_expired_filter")

    def is_expired_filter(self, queryset, name, value):
        today = date.today()
        return queryset.filter(due_date__lt=today).exclude(status="Converted")

    class Meta:
        model = Quotation
        fields = ()
