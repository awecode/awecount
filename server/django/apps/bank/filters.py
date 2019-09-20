from django_filters import MultipleChoiceFilter

from apps.bank.models import ChequeDeposit
from apps.tax.models import STATUSES
from apps.voucher.filters import DateFilterSet


class ChequeDepositFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=STATUSES)

    class Meta:
        model = ChequeDeposit
        fields = ()
