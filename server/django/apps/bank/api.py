from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bank.models import BankAccount, ChequeDeposit, ChequeDepositRow
from apps.bank.serializers import BankAccountSerializer, ChequeDepositCreateSerializer, ChequeDepositListSerializer, \
    ChequeVoucherSerializer, BankAccountChequeVoucherSerializer
from apps.ledger.models import Party
from apps.ledger.serializers import PartyMinSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, DeleteRows


class BankAccountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class ChequeDepositViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = ChequeDeposit.objects.all()
    serializer_class = ChequeDepositCreateSerializer
    model = ChequeDeposit
    row = ChequeDepositRow

    def get_queryset(self):
        queryset = super(ChequeDepositViewSet, self).get_queryset()
        return queryset.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return ChequeDepositListSerializer
        return ChequeDepositCreateSerializer

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(ChequeDeposit, request.company_id)
        return Response({'voucher_no': voucher_no})


class ChequeVoucherViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = ChequeVoucherSerializer
    collections = (
        ('bank_accounts', BankAccount, BankAccountChequeVoucherSerializer),
        ('parties', Party, PartyMinSerializer),
    )
