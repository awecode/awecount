from django_filters import MultipleChoiceFilter

from apps.bank.models import ChequeDeposit, ChequeIssue, FundTransfer
from apps.voucher.filters import DateFilterSet


class ChequeDepositFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=ChequeDeposit.STATUSES)

    class Meta:
        model = ChequeDeposit
        fields = ('bank_account',)


class ChequeIssueFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=ChequeIssue.STATUSES)

    class Meta:
        model = ChequeIssue
        fields = ('bank_account',)


class FundTransferFilterSet(DateFilterSet):
    status = MultipleChoiceFilter(choices=ChequeIssue.STATUSES)

    class Meta:
        model = FundTransfer
        fields = ('status', 'date')
