from django_filters import MultipleChoiceFilter

from apps.bank.models import ChequeDeposit, ChequeIssue
from apps.voucher.filters import DateFilterSet


class ChequeDepositFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=ChequeDeposit.STATUSES)

    class Meta:
        model = ChequeDeposit
        fields = ()


class ChequeIssueFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=ChequeIssue.STATUSES)

    class Meta:
        model = ChequeIssue
        fields = ()
