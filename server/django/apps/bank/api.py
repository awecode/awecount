from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.bank.filters import ChequeDepositFilterSet, ChequeIssueFilterSet
from apps.bank.models import BankAccount, ChequeDeposit, BankCashDeposit
from apps.bank.serializers import BankAccountSerializer, ChequeDepositCreateSerializer, ChequeDepositListSerializer, \
    ChequeIssueSerializer, BankAccountChequeIssueSerializer, BankCashDepositCreateSerializer, \
    BankCashDepositListSerializer
from apps.ledger.models import Party, Account
from apps.ledger.serializers import PartyMinSerializer, JournalEntriesSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin


class BankAccountViewSet(InputChoiceMixin, CRULViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class ChequeDepositViewSet(InputChoiceMixin, CRULViewSet):
    queryset = ChequeDeposit.objects.all()
    serializer_class = ChequeDepositCreateSerializer
    model = ChequeDeposit
    collections = [
        ('benefactors',
         Account.objects.only('id', 'name', ).filter(
             Q(category__name='Customers') | Q(category__name='Bank Accounts'))),
        ('bank_accounts', BankAccount.objects.filter(is_wallet=False).only('short_name', 'account_number')),
    ]

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'bank_account__bank_name', 'bank_account__account_number', 'benefactor__name',
                     'deposited_by', 'cheque_number', 'drawee_bank']
    filterset_class = ChequeDepositFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.select_related('benefactor', 'bank_account')
        return qs.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return ChequeDepositListSerializer
        return ChequeDepositCreateSerializer

    @action(detail=True, methods=['POST'])
    def mark_as_cleared(self, request, pk):
        cheque_deposit = self.get_object()
        if cheque_deposit.status == 'Issued':
            cheque_deposit.clear()
            return Response({})
        else:
            raise APIException('This voucher cannot be mark as cleared!')

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        cheque_deposit = self.get_object()
        cheque_deposit.cancel()
        return Response({})

    @action(detail=True)
    def details(self, request, pk):
        qs = self.get_queryset().select_related('benefactor', 'bank_account')
        data = ChequeDepositCreateSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        return Response(data)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        journals = obj.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)


class ChequeIssueViewSet(CRULViewSet):
    serializer_class = ChequeIssueSerializer
    collections = (
        ('bank_accounts', BankAccount.objects.filter(is_wallet=False), BankAccountChequeIssueSerializer),
        ('parties', Party, PartyMinSerializer),
        ('accounts', Account),
    )
    filterset_class = ChequeIssueFilterSet
    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['cheque_no', 'bank_account__bank_name', 'bank_account__account_number', 'party__name',
                     'issued_to', 'dr_account__name', 'amount']

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.cancel()
        return Response({})

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.select_related('party')
        return qs.order_by('-pk')


class CashDepositViewSet(CRULViewSet):
    queryset = BankCashDeposit.objects.all()
    serializer_class = BankCashDepositCreateSerializer
    model = BankCashDeposit

    collections = [
        ('benefactors',
         Account.objects.only('id', 'name', ).filter(
             Q(category__name='Customers') | Q(category__name='Bank Accounts'))),
        ('bank_accounts', BankAccount.objects.filter(is_wallet=False).only('short_name', 'account_number')),
    ]

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'bank_account__bank_name', 'bank_account__account_number', 'benefactor__name',
                     'deposited_by', ]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.select_related('benefactor', 'bank_account')
        return qs.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return BankCashDepositListSerializer
        return BankCashDepositCreateSerializer
