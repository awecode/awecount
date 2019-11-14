import datetime

from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bank.filters import ChequeDepositFilterSet
from apps.bank.models import BankAccount, ChequeDeposit
from apps.bank.serializers import BankAccountSerializer, ChequeDepositCreateSerializer, ChequeDepositListSerializer, \
    ChequeIssueSerializer, BankAccountChequeIssueSerializer
from apps.ledger.models import Party, Account
from apps.ledger.serializers import PartyMinSerializer, JournalEntriesSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, DeleteRows

from rest_framework import filters as rf_filters
from django_filters import rest_framework as filters


class BankAccountViewSet(InputChoiceMixin, CRULViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class ChequeDepositViewSet(InputChoiceMixin, CRULViewSet):
    queryset = ChequeDeposit.objects.all()
    serializer_class = ChequeDepositCreateSerializer
    model = ChequeDeposit
    collections = [
        ('benefactors', Account.objects.only('id', 'name', ).filter(category__name='Customers')),
        ('bank_accounts', BankAccount.objects.only('short_name', 'account_number')),
    ]

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'bank_account__bank_name', 'bank_account__account_number', 'benefactor__name',
                     'deposited_by', ]
    filterset_class = ChequeDepositFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
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
            cheque_deposit.clearing_date = datetime.datetime.today()
            cheque_deposit.save()
            cheque_deposit.apply_transactions()
            return Response({})
        else:
            raise APIException('This voucher cannot be mark as cleared!')

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        cheque_deposit = self.get_object()
        cheque_deposit.status = 'Cancelled'
        cheque_deposit.save()
        cheque_deposit.cancel_transactions()
        return Response({})

    @action(detail=True)
    def details(self, request, pk):
        qs = self.get_queryset()
        data = ChequeDepositCreateSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_cheque_deposit_update
        return Response(data)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        journals = obj.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)


class ChequeIssueViewSet(CRULViewSet):
    serializer_class = ChequeIssueSerializer
    collections = (
        ('bank_accounts', BankAccount, BankAccountChequeIssueSerializer),
        ('parties', Party, PartyMinSerializer),
    )
