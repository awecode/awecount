from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bank.models import BankAccount, ChequeDeposit, ChequeDepositRow
from apps.bank.serializers import BankAccountSerializer, ChequeDepositCreateSerializer, ChequeDepositListSerializer, \
    ChequeIssueSerializer, BankAccountChequeVoucherSerializer
from apps.ledger.models import Party
from apps.ledger.serializers import PartyMinSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, DeleteRows


class BankAccountViewSet(InputChoiceMixin, CRULViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class ChequeDepositViewSet(InputChoiceMixin, DeleteRows, CRULViewSet):
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

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset()
        data = ChequeDepositCreateSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_cheque_deposit_update
        return Response(data)

    @action(detail=True, methods=['POST'])
    def mark_as_cleared(self, request, pk):
        cheque_deposit = self.get_object()
        if cheque_deposit.status == 'Issued':
            cheque_deposit.status = 'Cleared'
            cheque_deposit.save()
            return Response({})
        else:
            raise APIException('This voucher cannot be mark as cleared!')


    @action(detail=True)
    def details(self, request, pk):
        qs = self.get_queryset()
        data = ChequeDepositCreateSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_cheque_deposit_update
        return Response(data)


class ChequeIssueViewSet(CRULViewSet):
    serializer_class = ChequeIssueSerializer
    collections = (
        ('bank_accounts', BankAccount, BankAccountChequeVoucherSerializer),
        ('parties', Party, PartyMinSerializer),
    )
