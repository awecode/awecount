from django_filters import MultipleChoiceFilter

from apps.tax.models import STATUSES, TaxPayment
from apps.voucher.filters import DateFilterSet


class TaxPaymentFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = TaxPayment
        fields = ()
