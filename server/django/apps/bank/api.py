from itertools import combinations

from django.db.models import Case, Q, When
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.aggregator.views import qs_to_xls
from apps.bank.filters import (
    ChequeDepositFilterSet,
    ChequeIssueFilterSet,
    FundTransferFilterSet,
)
from apps.bank.models import (
    BankAccount,
    BankCashDeposit,
    BankReconciliation,
    ChequeDeposit,
    FundTransferTemplate,
)
from apps.bank.resources import ChequeIssueResource
from apps.bank.serializers import (
    BankAccountChequeIssueSerializer,
    BankAccountSerializer,
    BankAccountWithLedgerSerializer,
    BankCashDepositCreateSerializer,
    BankCashDepositListSerializer,
    BankReconciliationSerializer,
    BankReconciliationStatementImportSerializer,
    ChequeDepositCreateSerializer,
    ChequeDepositListSerializer,
    ChequeIssueFormSerializer,
    ChequeIssueSerializer,
    FundTransferListSerializer,
    FundTransferSerializer,
    FundTransferTemplateSerializer,
)
from apps.ledger.models import Account, Party
from apps.ledger.serializers import JournalEntriesSerializer, PartyMinSerializer
from apps.ledger.models.base import Transaction
from awecount.libs.CustomViewSet import CRULViewSet, GenericSerializer
from awecount.libs.mixins import InputChoiceMixin


class BankAccountViewSet(InputChoiceMixin, CRULViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class ChequeDepositViewSet(InputChoiceMixin, CRULViewSet):
    queryset = ChequeDeposit.objects.all()
    serializer_class = ChequeDepositCreateSerializer
    model = ChequeDeposit
    collections = [
        (
            "benefactors",
            Account.objects.only(
                "id",
                "name",
            ).filter(Q(category__name="Customers") | Q(category__name="Bank Accounts")),
            GenericSerializer,
            True,
            ['name'],
        ),
        (
            "bank_accounts",
            BankAccount.objects.filter(is_wallet=False).only(
                "short_name", "account_number"
            ),
            GenericSerializer,
            True,
            ["short_name", "account_number", "bank_name"],
        ),
    ]

    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]
    search_fields = [
        "voucher_no",
        "bank_account__bank_name",
        "bank_account__account_number",
        "benefactor__name",
        "deposited_by",
        "cheque_number",
        "drawee_bank",
    ]
    filterset_class = ChequeDepositFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.select_related("benefactor", "bank_account")
        return qs.order_by("-pk")

    def get_serializer_class(self):
        if self.action == "list" or self.action in ("choices",):
            return ChequeDepositListSerializer
        return ChequeDepositCreateSerializer

    @action(detail=True, methods=["POST"])
    def mark_as_cleared(self, request, pk):
        cheque_deposit = self.get_object()
        if cheque_deposit.status == "Issued":
            cheque_deposit.clear()
            return Response({})
        else:
            raise APIException("This voucher cannot be mark as cleared!")

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk):
        cheque_deposit = self.get_object()
        cheque_deposit.cancel()
        return Response({})

    @action(detail=True)
    def details(self, request, pk):
        qs = self.get_queryset().select_related("benefactor", "bank_account")
        data = ChequeDepositCreateSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        return Response(data)

    @action(detail=True, url_path="journal-entries")
    def journal_entries(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        journals = obj.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)


class ChequeIssueViewSet(CRULViewSet):
    serializer_class = ChequeIssueSerializer
    collections = (
        (
            "bank_accounts",
            BankAccount.objects.filter(is_wallet=False),
            BankAccountChequeIssueSerializer,
            True,
            ['short_name', 'account_number', 'bank_name'],
        ),
        ("parties", Party, PartyMinSerializer, True, ['name']),
        ("accounts", Account, GenericSerializer, True, ['name']),
    )
    filterset_class = ChequeIssueFilterSet
    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]
    search_fields = [
        "cheque_no",
        "bank_account__bank_name",
        "bank_account__account_number",
        "party__name",
        "issued_to",
        "dr_account__name",
        "amount",
    ]

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.cancel()
        return Response({})

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ["list", "export"]:
            qs = qs.select_related("party")
        return qs.order_by("-pk")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ChequeIssueFormSerializer
        return super().get_serializer_class()

    @action(detail=False)
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset()).annotate(
            issued=Case(
                When(issued_to__isnull=True, then="party__name"), default="issued_to"
            )
        )
        params = [
            ("Invoices", queryset, ChequeIssueResource),
        ]
        return qs_to_xls(params)


class FundTransferViewSet(CRULViewSet):
    serializer_class = FundTransferSerializer
    list_serializer_class = FundTransferListSerializer

    collections = (
        (
            "from_account",
            Account.objects.filter(
                Q(category__name="Bank Accounts", category__default=True)
                | Q(category__name="Customers", category__default=True)
            ).order_by("category__name"),
            GenericSerializer,
            True,
            ['name'],
        ),
        (
            "to_account",
            Account.objects.filter(
                Q(category__name="Bank Accounts", category__default=True)
                | Q(category__name="Suppliers", category__default=True)
            ).order_by("category__name"),
            GenericSerializer,
            True,
            ['name'],
        ),
        (
            "transaction_fee_account",
            Account.objects.filter(
                category__name="Bank Charges", category__default=True
            ),
            GenericSerializer,
            True,
            ['name'],
        ),
    )

    filterset_class = FundTransferFilterSet
    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]
    search_fields = [
        "voucher_no",
        "from_account__name",
        "to_account__name",
        "transaction_fee_account__name",
        "amount",
        "transaction_fee",
    ]

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.cancel()
        return Response({})

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.select_related("from_account", "to_account")
        return qs.order_by("-pk")

    @action(detail=True, url_path="journal-entries")
    def journal_entries(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        journals = obj.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated_response = self.get_paginated_response(serializer.data)
        data = paginated_response.data
        templates = FundTransferTemplate.objects.filter(company=request.company).select_related("from_account", "to_account", "transaction_fee_account")
        data["templates"] = FundTransferTemplateSerializer(templates, many=True).data
        return Response(data)


class CashDepositViewSet(CRULViewSet):
    queryset = BankCashDeposit.objects.all()
    serializer_class = BankCashDepositCreateSerializer
    model = BankCashDeposit

    collections = [
        (
            "benefactors",
            Account.objects.only(
                "id",
                "name",
            ).filter(Q(category__name="Customers") | Q(category__name="Bank Accounts")),
            GenericSerializer,
            True,
            ['name'],
        ),
        (
            "bank_accounts",
            BankAccount.objects.filter(is_wallet=False).only(
                "short_name", "account_number"
            ),
            GenericSerializer,
            True,
            ['name'],
        ),
    ]

    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]
    search_fields = [
        "voucher_no",
        "bank_account__bank_name",
        "bank_account__account_number",
        "benefactor__name",
        "deposited_by",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.select_related("benefactor", "bank_account")
        return qs.order_by("-pk")

    def get_serializer_class(self):
        if self.action == "list" or self.action in ("choices",):
            return BankCashDepositListSerializer
        return BankCashDepositCreateSerializer

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.cancel()
        return Response({})

    @action(detail=True, url_path="journal-entries")
    def journal_entries(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        journals = obj.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk):
        obj = self.get_object()
        obj.cancel()
        return Response({})


class BankReconciliationViewSet(CRULViewSet):
    queryset = BankReconciliation.objects.all()
    serializer_class = BankReconciliationSerializer
    model = BankReconciliation

    def reconcile(self, company, statement_transactions, start_date, end_date, account_id):
        system_transactions = Transaction.objects.filter(
        company=company, journal_entry__date__range=[start_date, end_date], account_id=account_id
        ).order_by("journal_entry__date").select_related("journal_entry")
        
        # get system_transactions sql query
        print(system_transactions.query)
        
        def parse_amount(amount):
            if amount and isinstance(amount, str):
                return float(amount.replace(",", ""))
            return amount or 0
        
        # Prase statement transactions dr_amount and cr_amount
        for statement_transaction in statement_transactions:
            statement_transaction['dr_amount'] = parse_amount(statement_transaction.get('dr_amount'))
            statement_transaction['cr_amount'] = parse_amount(statement_transaction.get('cr_amount'))
            statement_transaction['balance'] = parse_amount(statement_transaction.get('balance'))
        
        
        reconciled_transactions = []
        unreconciled_statement_transactions = statement_transactions.copy()
        unreconciled_system_transactions = list(system_transactions)
        

        # Create a dictionary for quick lookup of system transactions by date
        system_transactions_by_date = {}
        for system_transaction in unreconciled_system_transactions:
            date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
            if date_str not in system_transactions_by_date:
                system_transactions_by_date[date_str] = []
            system_transactions_by_date[date_str].append(system_transaction)

        # iterate over statement transactions, if there is a matching system transaction, reconcile, add transaction_id to statement transaction
        for statement_transaction in statement_transactions:
            date_str = statement_transaction['date']
            if date_str in system_transactions_by_date:
                for system_transaction in system_transactions_by_date[date_str]:
                    if (
                        (statement_transaction.get('dr_amount') and 
                        statement_transaction['dr_amount'] == system_transaction.cr_amount) or
                        (statement_transaction.get('cr_amount') and 
                        statement_transaction['cr_amount'] == system_transaction.dr_amount)
                    ):
                        statement_transaction['transaction_ids'] = [system_transaction.pk]
                        reconciled_transactions.append(statement_transaction)
                        unreconciled_statement_transactions.remove(statement_transaction)
                        unreconciled_system_transactions.remove(system_transaction)
                        system_transactions_by_date[date_str].remove(system_transaction)
                        if not system_transactions_by_date[date_str]:
                            del system_transactions_by_date[date_str]
                        break
                    
        

        # in system_transactions that doesnt have transaction_id,
        # Reconcile transactions by sum
        for system_transaction in unreconciled_system_transactions:
            date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
            if date_str in system_transactions_by_date:
                # Filter statement transactions by date
                date_filtered_statement_transactions = [
                    t for t in unreconciled_statement_transactions if t['date'] == date_str
                ]
                # Try different combination lengths to match system transaction amount
                for r in range(1, len(date_filtered_statement_transactions) + 1):
                    for combination in combinations(date_filtered_statement_transactions, r):
                        # Calculate sum of debits and credits
                        total_dr = sum(t.get('dr_amount', 0) for t in combination)
                        total_cr = sum(t.get('cr_amount', 0) for t in combination)
                        
                        # Check if combination matches system transaction amount
                        if (total_dr == (system_transaction.cr_amount or 0) and 
                            total_cr == (system_transaction.dr_amount or 0)):
                            
                            # Mark these transactions as reconciled
                            for statement_transaction in combination:
                                statement_transaction['transaction_ids'] = [system_transaction.pk]
                                reconciled_transactions.append(statement_transaction)
                                unreconciled_statement_transactions.remove(statement_transaction)
                            
                            # Remove the system transaction from unreconciled list
                            unreconciled_system_transactions.remove(system_transaction)
                            system_transactions_by_date[date_str].remove(system_transaction)
                            if not system_transactions_by_date[date_str]:
                                del system_transactions_by_date[date_str]
                            break
                        
        # Reconcile transactions by sum
        for statement_transaction in unreconciled_statement_transactions:
            date_str = statement_transaction['date']
            if date_str in system_transactions_by_date:
                # Filter system transactions by date
                date_filtered_system_transactions = [
                    t for t in unreconciled_system_transactions if t.journal_entry.date.strftime('%Y-%m-%d') == date_str
                ]
                # Try different combination lengths to match statement transaction amount
                for r in range(1, len(date_filtered_system_transactions) + 1):
                    for combination in combinations(date_filtered_system_transactions, r):
                        # Calculate sum of debits and credits
                        total_dr = sum((t.dr_amount or 0) for t in combination)
                        total_cr = sum((t.cr_amount or 0) for t in combination)
                        
                        # Check if combination matches statement transaction amount
                        if (total_dr == float(statement_transaction.get('cr_amount', 0)) and 
                            total_cr == float(statement_transaction.get('dr_amount', 0))):
                            
                            # Mark these transactions as reconciled
                            for system_transaction in combination:
                                if statement_transaction.get('transaction_ids'):
                                    statement_transaction['transaction_ids'].append(system_transaction.pk)
                                else:
                                    statement_transaction['transaction_ids'] = [system_transaction.pk]
                                unreconciled_system_transactions.remove(system_transaction)
                                system_transactions_by_date[date_str].remove(system_transaction)
                            reconciled_transactions.append(statement_transaction)
                            
                            if not system_transactions_by_date[date_str]:
                                del system_transactions_by_date[date_str]
                            break
                        
        # Combine reconciled and unreconciled transactions into a single list
        bank_reconciliation_entries = []

        # Add reconciled transactions
        for statement_transaction in reconciled_transactions:
            bank_reconciliation_entries.append(BankReconciliation(
                company=company,
                statement_date=statement_transaction['date'],
                dr_amount=statement_transaction.get('dr_amount', None),
                cr_amount=statement_transaction.get('cr_amount', None),
                status='Reconciled',
                transaction_ids=statement_transaction.get('transaction_ids', []),
                bank_account_id=account_id,
                description=statement_transaction.get('description', None),
            ))

        # Add unreconciled transactions
        for statement_transaction in unreconciled_statement_transactions:
            bank_reconciliation_entries.append(BankReconciliation(
                company=company,
                statement_date=statement_transaction['date'],
                dr_amount=statement_transaction.get('dr_amount', None),
                cr_amount=statement_transaction.get('cr_amount', None),
                status='Unreconciled',
                bank_account_id=account_id,
                description=statement_transaction.get('description', None),
            ))

        # Perform bulk_create once
        BankReconciliation.objects.bulk_create(bank_reconciliation_entries,  batch_size=500)
                            
        return {
            'reconciled_transactions': reconciled_transactions,
            'unreconciled_statement_transactions': unreconciled_statement_transactions,
            'unreconciled_system_transactions': [
            {
                'id': t.pk,
                'date': t.journal_entry.date.strftime('%Y-%m-%d'),
                'dr_amount': t.dr_amount,
                'cr_amount': t.cr_amount,
            }
            for t in unreconciled_system_transactions
        ],
        }
                        

    @action(detail=False, url_path="banks")
    def get_banks(self, request):
        banks = BankAccount.objects.filter(company=request.company).only(
            "id", "short_name", "account_number", "ledger_id"
        )
        return Response(BankAccountWithLedgerSerializer(banks, many=True).data)


    @action(detail=False, url_path="import-statement", methods=["POST"])
    def import_statement(self, request):
        serializer = BankReconciliationStatementImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transactions = serializer.validated_data["transactions"]
        account_id = serializer.validated_data["bank_account"]
        response = self.reconcile(request.company, transactions, serializer.validated_data.get('start_date'), serializer.validated_data.get('end_date'), account_id)
        return Response(response)
