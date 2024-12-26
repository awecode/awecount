from collections import defaultdict
from datetime import datetime, timedelta
from itertools import chain, combinations

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Case, F, Q, When
from django.db.models.functions import Coalesce
from django.forms import ValidationError
from django_filters import rest_framework as filters
from django_q.tasks import async_task
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db.models import Subquery, OuterRef

from apps.aggregator.views import qs_to_xls
from apps.bank.filters import (
    ChequeDepositFilterSet,
    ChequeIssueFilterSet,
    FundTransferFilterSet,
)
from apps.bank.models import (
    BankAccount,
    BankCashDeposit,
    ChequeDeposit,
    FundTransfer,
    FundTransferTemplate,
    ReconciliationRow,
    ReconciliationRowTransaction,
    ReconciliationStatement,
)
from apps.bank.resources import ChequeIssueResource
from apps.bank.serializers import (
    BankAccountChequeIssueSerializer,
    BankAccountSerializer,
    BankAccountWithLedgerSerializer,
    BankCashDepositCreateSerializer,
    BankCashDepositListSerializer,
    ChequeDepositCreateSerializer,
    ChequeDepositListSerializer,
    ChequeIssueFormSerializer,
    ChequeIssueSerializer,
    FundTransferListSerializer,
    FundTransferSerializer,
    FundTransferTemplateSerializer,
    ReconciliationRowSerializer,
    ReconciliationStatementImportSerializer,
    ReconciliationStatementListSerializer,
    ReconciliationStatementSerializer,
)
from apps.ledger.models import Account, Party
from apps.ledger.models.base import JournalEntry, Transaction
from apps.ledger.serializers import (
    AccountMinSerializer,
    JournalEntriesSerializer,
    PartyMinSerializer,
    TransactionMinSerializer,
)
from apps.voucher.models import PaymentReceipt, SalesVoucher
from apps.voucher.serializers.sales import (
    PaymentReceiptFormSerializer,
    SalesVoucherMinListSerializer,
)
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


def reconcile(company_id, statement_transactions, start_date, end_date, account_id, email):
    try:
        start_date = start_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS)
        end_date = end_date + timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)
        system_transactions = Transaction.objects.filter(
        company_id=company_id, journal_entry__date__range=[start_date, end_date], account_id=account_id
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
            
            
        def reconcile_exact_match_single_transactions(statement_transaction, system_transactions):
            """
            Attempts to reconcile a single statement transaction with system transactions.

            Parameters:
                statement_transaction (dict): The statement transaction to reconcile.
                system_transactions (list): A list of system transactions to match against.

            Returns:
                bool: True if the transaction was reconciled, False otherwise.
            """
            for system_transaction in system_transactions:
                if (
                    (statement_transaction.get('dr_amount') and system_transaction.cr_amount and
                    abs(statement_transaction['dr_amount'] - system_transaction.cr_amount) < settings.BANK_RECONCILIATION_TOLERANCE) or
                    (statement_transaction.get('cr_amount') and system_transaction.dr_amount and
                    abs(statement_transaction['cr_amount'] - system_transaction.dr_amount) < settings.BANK_RECONCILIATION_TOLERANCE)
                ):
                    # Reconcile transactions
                    statement_transaction['transactions'] = [{'id': system_transaction.pk, 'updated_at': system_transaction.updated_at}]
                    statement_transaction['status'] = 'Reconciled'
                    reconciled_transactions.append(statement_transaction)
                    unreconciled_statement_transactions.remove(statement_transaction)
                    unreconciled_system_transactions.remove(system_transaction)
                    date_str = statement_transaction['date']
                    if date_str in system_transactions_by_date:
                        if system_transaction in system_transactions_by_date[date_str]:
                            system_transactions_by_date[date_str].remove(system_transaction)
                        
                        if not system_transactions_by_date[date_str]:
                            del system_transactions_by_date[date_str]
                    return True
            return False

        # iterate over statement transactions, if there is a matching system transaction, reconcile, add transaction_id to statement transaction
        for statement_transaction in statement_transactions:
            date_str = statement_transaction['date']
            if date_str in system_transactions_by_date:
                if reconcile_exact_match_single_transactions(statement_transaction, system_transactions_by_date[date_str]):
                    continue
                

        def reconcile_statement_combinations(system_transaction, statement_transactions, has_same_date=False):
            """
            Attempts to reconcile a single system transaction by finding combinations of statement transactions.

            Parameters:
                system_transaction (object): The system transaction to reconcile.
                statement_transactions (list): A list of statement transactions to match against.

            Returns:
                bool: True if the transaction was reconciled, False otherwise.
            """
            for r in range(2, len(statement_transactions) + 1):
                for combination in combinations(statement_transactions, r):
                    total_dr = sum(t.get('dr_amount', 0) for t in combination)
                    total_cr = sum(t.get('cr_amount', 0) for t in combination)

                    if (
                        abs(total_dr - (system_transaction.cr_amount or 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                        abs(total_cr - (system_transaction.dr_amount or 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                    ):
                        # Reconcile matched transactions
                        for statement_transaction in combination:
                            if statement_transaction.get('transactions'):
                                statement_transaction['transactions'].append({'id': system_transaction.pk, 'updated_at': system_transaction.updated_at})
                            else:
                                statement_transaction['transactions'] = [{'id': system_transaction.pk, 'updated_at': system_transaction.updated_at}]
                            if has_same_date:
                                statement_transaction['status'] = 'Reconciled'
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(statement_transaction)

                        unreconciled_system_transactions.remove(system_transaction)

                        date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
                        if date_str in system_transactions_by_date:
                            system_transactions_by_date[date_str].remove(system_transaction)
                            if not system_transactions_by_date[date_str]:
                                del system_transactions_by_date[date_str]

                        return True
            return False

        # in system_transactions that doesnt have transaction_id,
        # Reconcile transactions by sum
        for system_transaction in unreconciled_system_transactions[:]:  # Iterate over a copy to allow safe modification
            date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
            if date_str in system_transactions_by_date:
                # Filter statement transactions by date
                date_filtered_statement_transactions = [
                    t for t in unreconciled_statement_transactions if t['date'] == date_str
                ]

            if reconcile_statement_combinations(
                system_transaction,
                date_filtered_statement_transactions,
                has_same_date=True,
            ):
                continue
            
        def reconcile_system_combinations(statement_transaction, system_transactions, has_same_date=False):
            """
            Attempts to reconcile a single statement transaction by finding combinations of system transactions.

            Parameters:
                statement_transaction (dict): The statement transaction to reconcile.
                system_transactions (list): A list of system transactions to match against.

            Returns:
                bool: True if the transaction was reconciled, False otherwise.
            """
            # first group system transactions by its source_id by dr_amount and cr_amount
            system_transactions_by_source = {}
            for system_transaction in system_transactions:
                source_id = system_transaction.journal_entry.source_voucher_id
                if source_id not in system_transactions_by_source:
                    system_transactions_by_source[source_id] = []
                system_transactions_by_source[source_id].append(system_transaction)
                
            # loop over the grouped system transactions and try to reconcile
            for source_id, system_transactions in list(system_transactions_by_source.items()):
                for r in range(2, len(system_transactions) + 1):
                    for combination in combinations(system_transactions, r):
                        total_dr = sum((t.dr_amount or 0) for t in combination)
                        total_cr = sum((t.cr_amount or 0) for t in combination)

                        if (
                            abs(total_dr - statement_transaction.get('cr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                            abs(total_cr - statement_transaction.get('dr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                        ):
                            # Reconcile matched transactions
                            for system_transaction in combination:
                                if statement_transaction.get('transactions'):
                                    statement_transaction['transactions'].append({'id': system_transaction.pk, 'updated_at': system_transaction.updated_at})
                                else:
                                    statement_transaction['transactions'] = [{'id': system_transaction.pk, 'updated_at': system_transaction.updated_at}]
                                if has_same_date:
                                    statement_transaction['status'] = 'Reconciled'
                                unreconciled_system_transactions.remove(system_transaction)
                                system_transactions_by_date[system_transaction.journal_entry.date.strftime('%Y-%m-%d')].remove(system_transaction)

                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(statement_transaction)

                            return True
                        
                        elif (abs(total_dr - total_cr - statement_transaction.get('cr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE):
                            # dont remove the cr_amount transaction but remove the dr_amount transactions
                            for system_transaction in combination:
                                if statement_transaction.get('transactions'):
                                    statement_transaction['transactions'].append({'id': system_transaction.pk, 'updated_at': system_transaction.updated_at})
                                else:
                                    statement_transaction['transactions'] = [{'id': system_transaction.pk, 'updated_at': system_transaction.updated_at}]
                                if has_same_date:
                                    statement_transaction['status'] = 'Reconciled'
                                unreconciled_system_transactions.remove(system_transaction)
                                system_transactions_by_date[system_transaction.journal_entry.date.strftime('%Y-%m-%d')].remove(system_transaction)
      
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(statement_transaction)
                            return True
            
            
            for r in range(2, len(system_transactions) + 1):
                for combination in combinations(system_transactions, r):
                    total_dr = sum((t.dr_amount or 0) for t in combination)
                    total_cr = sum((t.cr_amount or 0) for t in combination)

                    if (
                        abs(total_dr - statement_transaction.get('cr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                        abs(total_cr - statement_transaction.get('dr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                    ):
                        # Reconcile matched transactions
                        for system_transaction in combination:
                            if statement_transaction.get('transactions'):
                                statement_transaction['transactions'].append({'id': system_transaction.pk, 'updated_at': system_transaction.updated_at})
                            else:
                                statement_transaction['transactions'] = [{'id': system_transaction.pk, 'updated_at': system_transaction.updated_at}]
                            if has_same_date:
                                statement_transaction['status'] = 'Reconciled'
                            unreconciled_system_transactions.remove(system_transaction)
                            system_transactions_by_date[system_transaction.journal_entry.date.strftime('%Y-%m-%d')].remove(system_transaction)

                        reconciled_transactions.append(statement_transaction)
                        unreconciled_statement_transactions.remove(statement_transaction)
                        
                        
                        return True
            return False
                        
        # Reconcile transactions by sum
        for statement_transaction in unreconciled_statement_transactions[:]:
            date_str = statement_transaction['date']
            if date_str in system_transactions_by_date:
                # Filter system transactions by date
                date_filtered_system_transactions = [
                    t for t in unreconciled_system_transactions if t.journal_entry.date.strftime('%Y-%m-%d') == date_str
                ]
                if reconcile_system_combinations(statement_transaction, date_filtered_system_transactions, has_same_date=True):
                    # Clean up empty dates
                    if not system_transactions_by_date[date_str]:
                        del system_transactions_by_date[date_str]
                    continue
                
                
        # def reconcile_system_statement_combinations(statement_transaction, system_transactions):

                        
                        
        # loop in unreconciled statement transactions and unreconciled system transactions, find combinations in system transaction of the date where debits - credits that match the statement transaction amount
        for i, statement_transaction in enumerate(
            unreconciled_statement_transactions[:]
        ):
            date_str = statement_transaction["date"]

            # Skip if no transactions for this date
            if date_str not in system_transactions_by_date:
                continue

            # Filter system transactions on the same date
            date_filtered_system_transactions = [
                t
                for t in unreconciled_system_transactions
                if t.journal_entry.date.strftime("%Y-%m-%d") == date_str
            ]

            # Validate statement transaction amount
            statement_amount = float(statement_transaction.get("cr_amount", 0))

            # Track if reconciliation is found
            reconciliation_found = False

            # Try combinations of system transactions
            for r in range(2, len(date_filtered_system_transactions) + 1):
                if reconciliation_found:
                    break

                for combination in combinations(date_filtered_system_transactions, r):
                    # Calculate net difference
                    net_difference = sum(
                        (t.dr_amount or 0) - (t.cr_amount or 0) for t in combination
                    )

                    # Check if net difference matches statement amount within tolerance
                    if (
                        abs(round(net_difference, 2) - round(statement_amount, 2))
                        < settings.BANK_RECONCILIATION_TOLERANCE
                    ):
                        # Mark transactions as reconciled
                        statement_transaction["transactions"] = [
                            # system_transaction.pk for system_transaction in combination
                            {"id": system_transaction.pk, "updated_at": system_transaction.updated_at} for system_transaction in combination
                        ]
                        statement_transaction["status"] = "Reconciled"

                        # Remove reconciled system transactions
                        for system_transaction in combination:
                            if system_transaction in unreconciled_system_transactions:
                                unreconciled_system_transactions.remove(
                                    system_transaction
                                )

                            # Remove from system transactions by date
                            if date_str in system_transactions_by_date:
                                if (
                                    system_transaction
                                    in system_transactions_by_date[date_str]
                                ):
                                    system_transactions_by_date[date_str].remove(
                                        system_transaction
                                    )

                        # Clean up empty date entries
                        if (
                            date_str in system_transactions_by_date
                            and not system_transactions_by_date[date_str]
                        ):
                            del system_transactions_by_date[date_str]

                        # Move to reconciled transactions
                        reconciled_transactions.append(statement_transaction)
                        unreconciled_statement_transactions.remove(
                            statement_transaction
                        )

                        reconciliation_found = True
                        break

                if reconciliation_found:
                    break
                
        
                
        # Iterate over unreconciled statement transactions to find direct matches
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
            date_range_start = statement_date
            date_range_end = statement_date + timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)

            # Filter system transactions within date range
            date_filtered_system_transactions = [
                t for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]
            if reconcile_exact_match_single_transactions(statement_transaction, date_filtered_system_transactions):
                continue

        # Reconcile system transactions by matching sums with statement transactions
        for system_transaction in unreconciled_system_transactions[:]:
            system_date = system_transaction.journal_entry.date
            date_range_start = system_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)
            date_range_end = system_date

            # Filter statement transactions within date range
            date_filtered_statement_transactions = [
                t for t in unreconciled_statement_transactions
                if date_range_start <= datetime.strptime(t['date'], '%Y-%m-%d').date() <= date_range_end
            ]

            # Check combinations of statement transactions
            if reconcile_statement_combinations(
                system_transaction,
                date_filtered_statement_transactions,
            ):
                continue

        # Final reconciliation by sums with a 3-day range for statement transactions
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
            date_range_start = statement_date
            date_range_end = statement_date + timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)

            # Filter system transactions
            date_filtered_system_transactions = [
                t for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]
            if reconcile_system_combinations(statement_transaction, date_filtered_system_transactions):
                continue
       
        # Iterate over unreconciled statement transactions to find direct matches
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
            date_range_start = statement_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS)
            date_range_end = statement_date

            # Filter system transactions within date range
            date_filtered_system_transactions = [
                t for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]
            if reconcile_exact_match_single_transactions(statement_transaction, date_filtered_system_transactions):
                continue

        # Reconcile system transactions by matching sums with statement transactions
        for system_transaction in unreconciled_system_transactions[:]:
            system_date = system_transaction.journal_entry.date
            date_range_start = system_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)
            date_range_end = system_date

            # Filter statement transactions within date range
            date_filtered_statement_transactions = [
                t for t in unreconciled_statement_transactions
                if date_range_start <= datetime.strptime(t['date'], '%Y-%m-%d').date() <= date_range_end
            ]

            # Check combinations of statement transactions
            if reconcile_statement_combinations(
                system_transaction,
                date_filtered_statement_transactions,
            ):
                continue

        # Final reconciliation by sums with a 3-day range for statement transactions
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
            date_range_start = statement_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS)
            date_range_end = statement_date

            # Filter system transactions
            date_filtered_system_transactions = [
                t for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]
            if reconcile_system_combinations(statement_transaction, date_filtered_system_transactions):
                continue
 
        # now compare the remaining unreconciled statement transactions and unreconciled system transactions, where system_transaction date can be within 3 days of statement_transaction date
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(
                statement_transaction["date"], "%Y-%m-%d"
            ).date()

            date_range_start = statement_date
            date_range_end = statement_date + timedelta(
                days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS
            )

            # Filter system transactions within the specified date range
            date_filtered_system_transactions = [
                t
                for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]

            # Skip if no system transactions in the date range
            if not date_filtered_system_transactions:
                continue

            # Group system transactions by date
            merged_system_transactions_by_date = {}
            for system_transaction in date_filtered_system_transactions:
                date_str = system_transaction.journal_entry.date.strftime("%Y-%m-%d")
                merged_system_transactions_by_date.setdefault(date_str, []).append(
                    system_transaction
                )

            reconciliation_found = False

            # Iterate through dates and transaction combinations
            for date_str, system_transactions_by_date in list(
                merged_system_transactions_by_date.items()
            ):
                if reconciliation_found:
                    break

                # Try combinations of 1 to all transactions on the date
                for r in range(2, len(system_transactions_by_date) + 1):
                    for combination in combinations(system_transactions_by_date, r):
                        # Calculate the net difference: debits - credits
                        net_difference = sum(
                            (t.dr_amount or 0) - (t.cr_amount or 0) for t in combination
                        )

                        # Get statement transaction amount safely
                        statement_amount = float(
                            statement_transaction.get(
                                "cr_amount", statement_transaction.get("dr_amount", 0)
                            )
                        )

                        # Check if the net difference matches the statement transaction amount
                        if (
                            abs(round(net_difference, 2) - round(statement_amount, 2))
                            < settings.BANK_RECONCILIATION_TOLERANCE
                        ):
                            # Mark these transactions as reconciled
                            statement_transaction.setdefault(
                                "transactions", []
                            ).extend(
                                {
                                    "transaction_id": t.pk,
                                    "updated_at": t.updated_at,
                                } for t in combination
                                if t.pk
                                not in {
                                    transaction["transaction_id"] for transaction in statement_transaction.get("transactions", [])
                                }
                            )

                            # Remove reconciled system transactions
                            for system_transaction in combination:
                                if (
                                    system_transaction
                                    in unreconciled_system_transactions
                                ):
                                    unreconciled_system_transactions.remove(
                                        system_transaction
                                    )

                            # Add to reconciled transactions and remove from unreconciled
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(
                                statement_transaction
                            )

                            # Update system transactions by date
                            merged_system_transactions_by_date[date_str] = [
                                t
                                for t in merged_system_transactions_by_date[date_str]
                                if t not in combination
                            ]

                            # Clean up empty date entries
                            if not merged_system_transactions_by_date[date_str]:
                                del merged_system_transactions_by_date[date_str]

                            reconciliation_found = True
                            break

                    if reconciliation_found:
                        break

        # now compare the remaining unreconciled statement transactions and unreconciled system transactions, where system_transaction date can be within 3 days of statement_transaction date
        for statement_transaction in unreconciled_statement_transactions[:]:
            statement_date = datetime.strptime(
                statement_transaction["date"], "%Y-%m-%d"
            ).date()

            date_range_start = statement_date - timedelta(
                days=settings.BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS
            )
            date_range_end = statement_date

            # Filter system transactions within the specified date range
            date_filtered_system_transactions = [
                t
                for t in unreconciled_system_transactions
                if date_range_start <= t.journal_entry.date <= date_range_end
            ]

            # Skip if no system transactions in the date range
            if not date_filtered_system_transactions:
                continue

            # Group system transactions by date
            merged_system_transactions_by_date = {}
            for system_transaction in date_filtered_system_transactions:
                date_str = system_transaction.journal_entry.date.strftime("%Y-%m-%d")
                merged_system_transactions_by_date.setdefault(date_str, []).append(
                    system_transaction
                )

            reconciliation_found = False

            # Iterate through dates and transaction combinations
            for date_str, system_transactions_by_date in list(
                merged_system_transactions_by_date.items()
            ):
                if reconciliation_found:
                    break

                # Try combinations of 1 to all transactions on the date
                for r in range(2, len(system_transactions_by_date) + 1):
                    for combination in combinations(system_transactions_by_date, r):
                        # Calculate the net difference: debits - credits
                        net_difference = sum(
                            (t.dr_amount or 0) - (t.cr_amount or 0) for t in combination
                        )

                        # Get statement transaction amount safely
                        statement_amount = float(
                            statement_transaction.get(
                                "cr_amount", statement_transaction.get("dr_amount", 0)
                            )
                        )

                        # Check if the net difference matches the statement transaction amount
                        if (
                            abs(round(net_difference, 2) - round(statement_amount, 2))
                            < settings.BANK_RECONCILIATION_TOLERANCE
                        ):
                            # Mark these transactions as reconciled
                            statement_transaction.setdefault("transactions", []).extend(
                                {
                                    "transaction_id": t.pk,
                                    "updated_at": t.updated_at,
                                }
                                for t in combination
                                if t.pk
                                not in {
                                    transaction["transaction_id"] for transaction in statement_transaction.get("transactions", [])
                                }
                            )

                            # Remove reconciled system transactions
                            for system_transaction in combination:
                                if (
                                    system_transaction
                                    in unreconciled_system_transactions
                                ):
                                    unreconciled_system_transactions.remove(
                                        system_transaction
                                    )

                            # Add to reconciled transactions and remove from unreconciled
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(
                                statement_transaction
                            )

                            # Update system transactions by date
                            merged_system_transactions_by_date[date_str] = [
                                t
                                for t in merged_system_transactions_by_date[date_str]
                                if t not in combination
                            ]

                            # Clean up empty date entries
                            if not merged_system_transactions_by_date[date_str]:
                                del merged_system_transactions_by_date[date_str]

                            reconciliation_found = True
                            break

                    if reconciliation_found:
                        break

        # Combine reconciled and unreconciled transactions into a single list
        with transaction.atomic():
            bank_reconciliation_entries = []
            
            # add to bank reconciliation
            bank_reconciliation_statement = ReconciliationStatement.objects.create(
                company_id=company_id,
                account_id=account_id,
                start_date=start_date,
                end_date=end_date,
            ) 

            bank_reconciliation_entries = []

            # Collect transactions to link after bulk creation
            reconciliation_transactions = []

            # Add reconciled transactions
            for statement_transaction in reconciled_transactions:
                reconciliation_row = ReconciliationRow(
                    date=statement_transaction['date'],
                    dr_amount=statement_transaction.get('dr_amount') or None,
                    cr_amount=statement_transaction.get('cr_amount') or None,
                    status=statement_transaction.get('status', 'Matched'),
                    balance=statement_transaction.get('balance', None),
                    statement_id=bank_reconciliation_statement.pk,
                    description=statement_transaction.get('description', None),
                )
                bank_reconciliation_entries.append(reconciliation_row)
                reconciliation_transactions.append(
                    (reconciliation_row, statement_transaction.get('transactions', []))
                )

            # Add unreconciled transactions
            for statement_transaction in unreconciled_statement_transactions:
                reconciliation_row = ReconciliationRow(
                    date=statement_transaction['date'],
                    dr_amount=statement_transaction.get('dr_amount') or None,
                    cr_amount=statement_transaction.get('cr_amount') or None,
                    status='Unreconciled',
                    balance=statement_transaction.get('balance', None),
                    statement_id=bank_reconciliation_statement.pk,
                    description=statement_transaction.get('description', None),
                )
                bank_reconciliation_entries.append(reconciliation_row)

            # Perform bulk_create
            ReconciliationRow.objects.bulk_create(
                bank_reconciliation_entries, batch_size=500
            )

            # Link transactions in bulk
            reconciliation_row_mapping = {row: transactions for row, transactions in reconciliation_transactions}

            # Prepare ReconciliationRowTransaction objects
            bulk_transactions = [
                ReconciliationRowTransaction(
                    reconciliation_row=row,
                    transaction_id=transaction["id"],
                    transaction_last_updated_at=transaction["updated_at"],
                )
                for row, transactions in reconciliation_row_mapping.items()
                for transaction in transactions
            ]

            # Perform bulk_create for transactions
            ReconciliationRowTransaction.objects.bulk_create(bulk_transactions, batch_size=500)

        # email the user
        header = "Bank Reconciliation Statement Import Completed"
        message = "Bank Reconciliation Statement Import Completed, with " + str(len(reconciled_transactions)) + " transactions reconciled and " + str(len(unreconciled_statement_transactions)) + " transactions unreconciled"
        send_mail(header, message, settings.DEFAULT_FROM_EMAIL, [email])
        return
    except Exception as e:
        header = "Bank Reconciliation Statement Import Failed"
        message = "Something went wrong, please contact support"
        send_mail(header, message, settings.DEFAULT_FROM_EMAIL, [email])
        return e

class ReconciliationViewSet(CRULViewSet):
    queryset = ReconciliationStatement.objects.all().prefetch_related("rows__transactions").order_by("-end_date")
    serializer_class = ReconciliationStatementSerializer
    model = ReconciliationStatement
    
    def get_serializer_class(self):
        if self.action == "list":
            return ReconciliationStatementListSerializer
        return self.serializer_class
    
    def filter_queryset(self, queryset):
        if self.action == 'retrieve':
            return queryset
        return super().filter_queryset(queryset)

    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]

    filterset_fields = [
        'account_id',
    ]

    search_fields = [
        'account__name',
        'start_date',
        'end_date',
    ]
    
    def filter_rows(self, rows, params):
        """
        Apply filtering logic to the rows queryset based on request parameters.
        """
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        status = params.get('status')
        search = params.get('search')
        
        filters = Q()

        # Filter by status
        if status:
                filters &= Q(status=status)

        # Search by description, amount, or date
        if search:
            filters &= (
                Q(description__icontains=search) |
                Q(dr_amount__icontains=search) |
                Q(cr_amount__icontains=search) |
                Q(date__icontains=search)
            )

        # Filter by date range
        if start_date or end_date:
            if not (start_date and end_date):
                raise ValidationError({"detail": "Both 'start_date' and 'end_date' must be provided for date filtering."})
            filters &= Q(date__range=[start_date, end_date])
            
        rows = rows.filter(filters)
        return rows

    def merge_transactions(self, statement_transactions, system_transactions):
        # Convert querysets to lists to avoid repeated database queries
        statements = list(statement_transactions)
        transactions = list(system_transactions)
        # 4. Create Mappings Using Dictionaries
        statement_to_systems_map = defaultdict(list)
        system_to_statements_map = defaultdict(list)

        transaction_dict = {t.id: t for t in transactions}

        for statement in statements:
            for transaction_id in statement.transaction_ids:
                system_transaction = transaction_dict.get(transaction_id)
                if system_transaction:
                    statement_to_systems_map[statement].append(system_transaction)
                    system_to_statements_map[system_transaction].append(statement)

        # 5. Group Transactions Efficiently
        merged_groups = []
        processed_statements = set()
        processed_systems = set()

        for statement, system_transactions in statement_to_systems_map.items():
            if statement in processed_statements:
                continue

            group = {"statement_transactions": [], "system_transactions": []}

            # Add current statement and its systems
            group["statement_transactions"].append(statement)
            processed_statements.add(statement)

            for system_transaction in system_transactions:
                if system_transaction not in processed_systems:
                    group["system_transactions"].append(system_transaction)
                    processed_systems.add(system_transaction)

                    # Add other statements related to this system
                    for other_statement in system_to_statements_map[system_transaction]:
                        if other_statement not in processed_statements:
                            group["statement_transactions"].append(other_statement)
                            processed_statements.add(other_statement)

            merged_groups.append(
                {
                    "statement_transactions": ReconciliationRowSerializer(
                        group["statement_transactions"], many=True
                    ).data,
                    "system_transactions": TransactionMinSerializer(
                        group["system_transactions"], many=True
                    ).data,
                }
            )

        # Add unprocessed statements (no matching system transactions)
        for statement in statements:
            if statement not in processed_statements:
                merged_groups.insert(0,
                    {
                        "statement_transactions": ReconciliationRowSerializer(
                            [statement], many=True
                        ).data,
                        "system_transactions": [],
                    }
                )

        # Add unprocessed system transactions (no matching statements)
        for system_transaction in transactions:
            if system_transaction not in processed_systems:
                merged_groups.insert(0,
                    {
                        "statement_transactions": [],
                        "system_transactions": TransactionMinSerializer(
                            [system_transaction], many=True
                        ).data,
                    }
                )

        return merged_groups

    def get_paginated_merged_transactions(self, bank_statements, company, account_id):
        page = self.paginate_queryset(bank_statements)
        all_transaction_ids = set(
            {data for entry in page for data in entry["transaction_ids"]}
        )
        all_statement_ids = set(
            {data for entry in page for data in entry["grouped_statements"]}
        )

        # Fetch system transactions based on transaction ids
        system_transactions = (
            Transaction.objects.filter(
                company=company,
                account_id=account_id,
                id__in=all_transaction_ids,
            )
            .order_by("journal_entry__date")
            .select_related("journal_entry__content_type")
            .prefetch_related(
                "journal_entry__transactions__account", "journal_entry__source"
            )
        )

        # Fetch reconciliation rows for the filtered statement ids
        statements_queryset = (
            ReconciliationRow.objects.filter(
                statement__company=company,
                statement__account_id=account_id,
                id__in=all_statement_ids,
            )
            .annotate(transaction_ids=ArrayAgg("transactions__transaction_id"))
            .select_related("statement")
        )
        merged_transactions = self.merge_transactions(
            statements_queryset, system_transactions
        )

        return self.get_paginated_response(merged_transactions)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Filter rows based on query parameters
        filtered_rows = self.filter_rows(instance.rows, request.query_params)

        matching_statement_ids = filtered_rows.values_list("pk", flat=True)
        bank_statements = (
            instance.rows
            .filter(pk__in=matching_statement_ids)
            .values("id")
            .annotate(
                grouped_statements=ArrayAgg("id", distinct=True),
                transaction_ids=Coalesce(
                    ArrayAgg("transactions__transaction_id", distinct=True), []
                ),
            ).order_by("-date")
        )

        return self.get_paginated_merged_transactions(bank_statements, request.company, instance.account_id)

    @action(detail=True, url_path="statement-info")
    def get_statement_info(self, request, pk):
        instance = self.get_object()
        data = {
            'account': AccountMinSerializer(instance.account).data,
            'date': {
                'start': instance.start_date,
                'end': instance.end_date
            },
            'total_reconciled': instance.rows.filter(status='Reconciled').count(),
            'total_unreconciled': instance.rows.filter(status='Unreconciled').count(),
        }
        return Response(data)
    
                        

    @action(detail=False, url_path="defaults")
    def get_defaults(self, request):
        banks = BankAccount.objects.filter(company=request.company).only(
            "id", "short_name", "account_number", "ledger_id"
        )
        return Response({ 'banks':BankAccountWithLedgerSerializer(banks, many=True).data, 'acceptable_difference':  settings.BANK_RECONCILIATION_TOLERANCE, 'adjustment_threshold': settings.BANK_RECONCILIATION_ADJUSTMENT_THRESHOLD })


    @action(detail=False, url_path="import-statement", methods=["POST"])
    def import_statement(self, request):
        serializer = ReconciliationStatementImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transactions = serializer.validated_data["transactions"]
        account_id = serializer.validated_data["account_id"]
        
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
         
        # Filter transactions if both start_date and end_date are provided
        if start_date and end_date:
            transactions = [
                transaction for transaction in transactions
                if start_date <= datetime.strptime(transaction['date'], '%Y-%m-%d').date() <= end_date
            ]

        # If not both start_date and end_date are provided, calculate them from the transaction dates
        if not start_date or not end_date:
            dates = [datetime.strptime(transaction['date'], '%Y-%m-%d').date() for transaction in transactions]
            if not start_date:
                start_date = min(dates)
            if not end_date:
                end_date = max(dates)
                
        # see if there is already a statement for the same account, which may conflict with the new statement
        existing_statement = ReconciliationStatement.objects.filter(
            company=request.company,
            account_id=account_id,
        ).filter(
          Q(start_date__lte=end_date, end_date__gte=start_date) 
        ).first()
        
        if existing_statement:
            raise APIException("Duplicate statement found for the same account and date range")
                

        # Ensure all transactions fall within the start_date and end_date range
        transactions = [
            transaction for transaction in transactions
            if start_date <= datetime.strptime(transaction['date'], '%Y-%m-%d').date() <= end_date
        ]
        async_task(
            reconcile,
            request.company_id,
            transactions,
            start_date,
            end_date,
            account_id,
            request.user.email,
        )
        
        return Response({})
    @action(detail=False, url_path="matched-transactions")
    def matched_transactions(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account_id")

        if not start_date or not end_date or not account_id:
            raise APIException("start_date, end_date and account_id are required")

        bank_statements = (
            ReconciliationRow.objects.filter(
                statement__company=request.company,
                statement__account_id=account_id,
                date__range=[start_date, end_date],
                status="Matched",
            )
            .values("id")
            .annotate(
                grouped_statements=ArrayAgg("id", distinct=True),
                transaction_ids=Coalesce(
                    ArrayAgg("transactions__transaction_id", distinct=True), []
                ),
            ).order_by("-date")
        )

        return self.get_paginated_merged_transactions(bank_statements, request.company, account_id)

    @action(detail=False, url_path="unreconciled-bank-transactions")
    def unreconciled_bank_transactions(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account_id")

        if not start_date or not end_date or not account_id:
            raise APIException("start_date, end_date and account_id are required")

        search = request.query_params.get("search")
        sort_by = request.query_params.get("sort_by")
        sort_dir = request.query_params.get("sort_dir")

        if sort_by not in ["date", "dr_amount", "cr_amount"]:
            sort_by = "date"

        if sort_dir == "desc":
            sort_by = "-" + sort_by

        filters = Q(
            statement__company=request.company,
            statement__account_id=account_id,
            date__range=[start_date, end_date],
            status="Unreconciled",
        )
        if search:
            filters &= (
                Q(description__icontains=search)
                | Q(dr_amount__icontains=search)
                | Q(cr_amount__icontains=search)
            )

        entries = ReconciliationRow.objects.filter(filters).order_by(sort_by)
        # send paginated response
        page = self.paginate_queryset(entries)
        serializer = ReconciliationRowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="unreconciled-system-transactions")
    def unreconciled_system_transactions(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        account_id = request.query_params.get("account_id")

        if not start_date or not end_date or not account_id:
            raise APIException("start_date, end_date and account_id are required")

        search = request.query_params.get("search")
        sort_by = request.query_params.get("sort_by")
        sort_dir = request.query_params.get("sort_dir")

        if sort_by not in ["dr_amount", "cr_amount"]:
            sort_by = "journal_entry__date"

        if sort_dir == "desc":
            sort_by = "-" + sort_by

        reconciled_transaction_ids = ReconciliationRowTransaction.objects.filter(
            reconciliation_row__statement__company=request.company,
            reconciliation_row__statement__account_id=account_id,
        ).values_list("transaction_id", flat=True).distinct()


        filters = Q(
            company=request.company,
            journal_entry__date__range=[start_date, end_date],
            account_id=account_id,
        )
        if search:
            filters &= (
                Q(dr_amount__icontains=search)
                | Q(cr_amount__icontains=search)
                | Q(journal_entry__transactions__account__name__icontains=search)
                | Q(journal_entry__transactions__dr_amount__icontains=search)
                | Q(journal_entry__transactions__cr_amount__icontains=search)
            )

        unreconciled_system_transactions = (
            Transaction.objects.filter(filters)
            .exclude(id__in=reconciled_transaction_ids)
            .order_by(sort_by)
            .select_related("journal_entry__content_type")
            .prefetch_related(
                "journal_entry__transactions__account",
            )
            .distinct()
        )

        # return paginated response
        page = self.paginate_queryset(unreconciled_system_transactions)
        serializer = TransactionMinSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # @action(detail=False, url_path="unreconciled-bank-transactions")
    # def unreconciled_bank_transactions(self, request):
    #     start_date = request.query_params.get('start_date')
    #     end_date = request.query_params.get('end_date')
    #     account_id = request.query_params.get('account_id')
        
    #     if not start_date or not end_date or not account_id:
    #         raise APIException("start_date, end_date and account_id are required")

    #     # Fetch reconciled transaction IDs for the same company, account, and date
    #     reconciled_transaction_ids = ReconciliationRow.objects.filter(
    #         statement__company=request.company,
    #         statement__account_id=account_id,
    #         status='Reconciled'
    #     ).values_list('transaction_ids', flat=True)

    #     reconciled_transaction_ids_set = set(chain.from_iterable(reconciled_transaction_ids))

    #     transactions = Transaction.objects.filter(
    #         company=request.company,
    #         journal_entry__date__range=[start_date, end_date],
    #         account_id=account_id
    #     ).exclude(
    #         id__in=reconciled_transaction_ids_set
    #     ).order_by("journal_entry__date").select_related("journal_entry__content_type").prefetch_related(
    #         "journal_entry__transactions__account",
    #         "journal_entry__source"
    #     )

    #     # fetch bank reconciliation entries
    #     bank_statements = ReconciliationRow.objects.filter(
    #         statement__company=request.company, statement__account_id=account_id, date__range=[start_date, end_date],
    #         status__in=['Unreconciled', 'Matched']
    #     ).order_by("date")
        
    #     return Response({ 'system_transactions': TransactionMinSerializer(transactions, many=True).data, 'statement_transactions': ReconciliationEntriesSerializer(bank_statements, many=True).data, 'acceptable_difference':  settings.BANK_RECONCILIATION_TOLERANCE, 'adjustment_threshold': settings.BANK_RECONCILIATION_ADJUSTMENT_THRESHOLD })
    
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions")
    def reconcile_transactions(self, request):
        statement_ids = request.data.get('statement_ids')
        transaction_ids = request.data.get('transaction_ids')
        if not statement_ids or not transaction_ids:
            raise ValidationError({"detail": "statement_ids and transaction_ids are required"})
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        transaction_objects = Transaction.objects.filter(id__in=transaction_ids)
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        transaction_sum = sum([obj.dr_amount - (obj.cr_amount or 0) if obj.dr_amount else -obj.cr_amount for obj in transaction_objects])
        if abs(entries_sum - transaction_sum) > settings.BANK_RECONCILIATION_TOLERANCE:
            raise ValidationError({"detail": "Difference between statement transactions and system transactions is too large for reconciliation"})
        entries.update(status='Reconciled')
        # create reconciliation row transactions for the entries
        to_create = []
        for obj in entries:
            for transaction_data in transaction_objects:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
                
        ReconciliationRowTransaction.objects.bulk_create(to_create)
        return Response({})
    
    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="unmatch-transactions")
    def unmatch_transactions(self, request):
        statement_ids = request.data.get("statement_ids")
        if not statement_ids or not isinstance(statement_ids, list):
            raise ValidationError({"detail": "A list of 'statement_ids' is required."})
        
        # Fetch ReconciliationRow entries matching the provided statement IDs
        entries = ReconciliationRow.objects.filter(id__in=statement_ids)
        if not entries.exists():
            raise ValidationError({"detail": "No matching reconciliation rows found."})

        # Check for transactions linked to the specified statement IDs
        invalid_transactions = ReconciliationRowTransaction.objects.filter(
            transaction_id__in=entries.values_list("transactions__transaction_id", flat=True),
        ).exclude(reconciliation_row_id__in=statement_ids).exists()
        
        if invalid_transactions:
            raise ValidationError({
                "detail": "Some statement_ids have transactions linked to other statements."
            })

        # Update the status of the entries to 'Unreconciled'
        entries.update(status="Unreconciled")

        # Delete related transactions for the entries
        ReconciliationRowTransaction.objects.filter(reconciliation_row_id__in=statement_ids).delete()

        # Delete journal entries associated with the entries
        JournalEntry.objects.filter(
            content_type__model="reconciliationrow",
            object_id__in=entries.values_list("id", flat=True)
        ).delete()

        return Response({"detail": "Transactions successfully unmatched."})
    
    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="delete-transactions")
    def delete_transactions(self, request):
        # Retrieve and validate `statement_ids` from the request
        statement_ids = request.data.get("statement_ids")
        if not statement_ids or not isinstance(statement_ids, list):
            raise ValidationError({"detail": "A list of 'statement_ids' is required."})
        
        # Fetch ReconciliationRow entries matching the provided statement IDs
        entries = ReconciliationRow.objects.filter(id__in=statement_ids)
        if not entries.exists():
            raise ValidationError({"detail": "No matching reconciliation rows found."})

        # Ensure that all provided `statement_ids` have associated transactions only within the scope of the given IDs
        invalid_transactions = ReconciliationRowTransaction.objects.filter(
            transaction_id__in=entries.values_list("transactions__transaction_id", flat=True),
        ).exclude(reconciliation_row_id__in=statement_ids).exists()

        if invalid_transactions:
            raise ValidationError({
                "detail": "Some statement_ids have transactions linked to other statements."
            })
        
        JournalEntry.objects.filter(
            content_type__model="reconciliationrow",
            object_id__in=entries.values_list("id", flat=True)
        ).delete()
        
        entries.delete()
        return Response({"detail": "Transactions successfully deleted."})
    
    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="reconcile-with-adjustment")
    def reconcile_with_adjustment(self, request):
        statement_ids = request.data.get('statement_ids')
        transaction_ids = request.data.get('transaction_ids')
        narration = request.data.get('narration')
        # TODO: max number of statement_ids
        if not statement_ids or not transaction_ids or not narration or len(statement_ids) > 10:
            raise ValidationError({"detail": "statement_ids, transaction_ids and narration are required and statement_ids should be less than 10"})
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        
        transaction_objects = Transaction.objects.filter(id__in=transaction_ids).select_related("journal_entry")
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        transaction_sum = sum([obj.dr_amount - (obj.cr_amount or 0) if obj.dr_amount else -obj.cr_amount for obj in transaction_objects])
        
        # find the difference
        difference = entries_sum - transaction_sum
        # validate the difference
        if abs(difference) > settings.BANK_RECONCILIATION_ADJUSTMENT_THRESHOLD:
            raise ValidationError({"detail": "Difference between statement transactions and system transactions is too large for reconciliation"})
        # Divide the difference by the number of statement transactions and put the difference in the adjustment field
        latest_date = max(
            (obj.journal_entry.date for obj in transaction_objects if obj.journal_entry and obj.journal_entry.date),
        )
        adjustment = difference / len(entries)
        entries.update(adjustment_amount=adjustment, status='Reconciled')

        adjustment_account = Account.objects.get(
            name="Bank Reconciliation Adjustment", company=self.request.company
        )
        bank_account = entries[0].statement.account
        
        # Create transaction for the adjustment
        for obj in entries:
            obj.apply_transactions(adjustment_account, latest_date)

        # get new transaction ids from journal entries
        transactions = Transaction.objects.filter(
            journal_entry__content_type__model="reconciliationrow",
            journal_entry__object_id__in=entries.values_list("id", flat=True),
            account_id=bank_account.id,
        ).values_list("id", "updated_at")
        to_create = []
        for obj in entries:
            for transaction_data in transaction_objects:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
            for transaction_data in transactions:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data[0], transaction_last_updated_at=transaction_data[1]))
            
        ReconciliationRowTransaction.objects.bulk_create(to_create)
           
        return Response({})
    
    @action(detail=False, url_path="sales-vouchers")
    def find_sales_vouchers(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            raise APIException("start_date and end_date are required")
        search = request.query_params.get('search')
        sort_by = request.query_params.get("sort_by")
        sort_dir = request.query_params.get("sort_dir")

        if sort_by not in ["total_amount"]:
            sort_by = "date"

        if sort_dir == "desc":
            sort_by = "-" + sort_by
            
        filters = Q(date__range=[start_date, end_date]) | Q(due_date__range=[start_date, end_date])
        if search:
            filters &= (
                Q(total_amount__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(party__name__icontains=search) |
                Q(party__tax_registration_number__icontains=search) |
                Q(voucher_no__icontains=search) |
                Q(remarks__icontains=search) 
            )
        
        sales_vouchers = SalesVoucher.objects.filter(
            company=request.company,
            mode='Credit',
            status='Issued',
            party__isnull=False
        ).filter(filters).order_by(sort_by)
        page = self.paginate_queryset(sales_vouchers)
        serializer = SalesVoucherMinListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    
    def create_payment_receipt(self, latest_entry_date, account_ids, entries, vouchers, remarks):
        bank_account = entries[0].statement.account.bank_accounts.first().id
        saved_vouchers = []
        for voucher in vouchers:
            data = {
                'date': latest_entry_date,
                'bank_account': bank_account,
                'amount': voucher.total_amount,
                'invoice_nos': [voucher.voucher_no],
                'invoices': [voucher.id],
                'party_id': voucher.party.id,
                'remarks': remarks,
                'mode': 'Bank Deposit',
            }
            serializer = PaymentReceiptFormSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['company'] = self.request.company
            saved_vouchers.append(serializer.save())
        return saved_vouchers
    
    
    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions-with-sales-vouchers")
    def reconcile_transactions_with_sales_vouchers(self, request):
        statement_ids = request.data.get('statement_ids')
        invoice_ids = request.data.get('invoice_ids')
        remarks = request.data.get('remarks')
        if not statement_ids or not invoice_ids:
            raise ValidationError({"detail": "statement_ids and invoice_ids are required"})
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        vouchers = SalesVoucher.objects.filter(id__in=invoice_ids)
        # validate if all the statement of the entries has same account_id
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        vouchers_sum = sum([obj.total_amount for obj in vouchers])
        if abs(entries_sum - vouchers_sum) > settings.BANK_RECONCILIATION_TOLERANCE:
            raise ValidationError({"detail": "Difference between statement transactions and invoices is too large for reconciliation"})
        
        latest_entry_date = max(obj.date for obj in entries)
        saved_vouchers= self.create_payment_receipt(latest_entry_date, account_ids, entries, vouchers, remarks)
        transactions = Transaction.objects.filter(journal_entry__content_type=ContentType.objects.get_for_model(PaymentReceipt), journal_entry__object_id__in=[voucher.id for voucher in saved_vouchers], account_id=next(iter(account_ids)))
        to_create = []
        for obj in entries:
            for transaction_data in transactions:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
                
        ReconciliationRowTransaction.objects.bulk_create(to_create)
        entries.update(status='Reconciled')
        return Response({})


    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions-with-sales-vouchers-and-adjustment")
    def reconcile_transactions_with_sales_vouchers_and_adjustment(self, request):
        statement_ids = request.data.get('statement_ids')
        invoice_ids = request.data.get('invoice_ids')
        remarks = request.data.get('remarks')
        if not statement_ids or not invoice_ids:
            raise ValidationError({"detail": "statement_ids and invoice_ids are required"})
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        vouchers = SalesVoucher.objects.filter(id__in=invoice_ids)
        # validate if all the statement of the entries has same account_id
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        vouchers_sum = sum([obj.total_amount for obj in vouchers])
        # find the difference
        difference = entries_sum - vouchers_sum
        # validate the difference
        if abs(difference) > settings.BANK_RECONCILIATION_ADJUSTMENT_THRESHOLD:
            raise ValidationError({"detail": "Difference between statement transactions and invoices is too large for reconciliation"})
        
        latest_entry_date = max(obj.date for obj in entries)
        saved_vouchers = self.create_payment_receipt(latest_entry_date, account_ids, entries, vouchers, remarks)
        transaction_objects = Transaction.objects.filter(journal_entry__content_type=ContentType.objects.get_for_model(PaymentReceipt), journal_entry__object_id__in=[voucher.id for voucher in saved_vouchers], account_id=next(iter(account_ids)))
                
        adjustment = difference / len(entries)
        entries.update(status='Reconciled', adjustment_amount=adjustment)
        adjustment_account = Account.objects.get(
            name="Bank Reconciliation Adjustment", company=self.request.company
        )
        bank_account = entries[0].statement.account
        
        # Create transaction for the adjustment
        for obj in entries:
            obj.apply_transactions(adjustment_account, latest_entry_date)

        # get new transaction ids from journal entries
        transactions = Transaction.objects.filter(
            journal_entry__content_type__model="reconciliationrow",
            journal_entry__object_id__in=entries.values_list("id", flat=True),
            account_id=bank_account.id,
        ).values_list("id", "updated_at")
        to_create = []
        for obj in entries:
            for transaction_data in transaction_objects:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
            for transaction_data in transactions:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data[0], transaction_last_updated_at=transaction_data[1]))
            
        ReconciliationRowTransaction.objects.bulk_create(to_create)
        return Response({})
    
    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions-with-funds-transfer")
    def reconcile_transactions_with_funds_transfer(self, request):
        statement_ids = request.data.get('statement_ids')
        if not statement_ids:
            raise ValidationError({"detail": "statement_ids are required"})
        serializer = FundTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # add company to the serializer
        serializer.validated_data['company'] = self.request.company
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        # validate if all the statement of the entries has same account_id
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        # amount of the funds transfer
        amount = serializer.validated_data['amount'] + serializer.validated_data.get('transaction_fee', 0)
        # Since we get negative amount for entries_sum, we need to reverse the sign
        if abs(entries_sum + amount) > settings.BANK_RECONCILIATION_TOLERANCE:
            raise ValidationError({"detail": "The sum of the statement transactions and of the funds transfer do not match"})
        response = serializer.save()
        transactions = Transaction.objects.filter(journal_entry__content_type=ContentType.objects.get_for_model(FundTransfer), journal_entry__object_id=response.id, account_id=next(iter(account_ids)))
        entries.update(status='Reconciled')
        to_create = []
        for obj in entries:
            for transaction_data in transactions:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
        ReconciliationRowTransaction.objects.bulk_create(to_create)
        return Response({})

    @transaction.atomic()
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions-with-cheque-issue")
    def reconcile_transactions_with_cheque_issue(self, request):
        statement_ids = request.data.get('statement_ids')
        if not statement_ids:
            raise ValidationError({"detail": "statement_ids are required"})
        serializer = ChequeIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # add company to the serializer
        serializer.validated_data['company'] = self.request.company
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        # validate if all the statement of the entries has same account_id
        account_ids = set([obj.statement.account_id for obj in entries])
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})
        
        entries_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in entries])
        # amount of the funds transfer
        amount = serializer.validated_data['amount']
        # Since we get negative amount for entries_sum, we need to reverse the sign
        if abs(entries_sum + amount) > settings.BANK_RECONCILIATION_TOLERANCE:
            raise ValidationError({"detail": "The sum of the statement transactions and of the cheque issue do not match"})
        response = serializer.save()
        transactions = Transaction.objects.filter(journal_entry__content_type=ContentType.objects.get_for_model(FundTransfer), journal_entry__object_id=response.id, account_id=next(iter(account_ids)))
        entries.update(status='Reconciled')
        to_create = []
        for obj in entries:
            for transaction_data in transactions:
                to_create.append(ReconciliationRowTransaction(reconciliation_row=obj, transaction_id=transaction_data.id, transaction_last_updated_at=transaction_data.updated_at))
        ReconciliationRowTransaction.objects.bulk_create(to_create)
        return Response({})
    
    
    @action(detail=True, url_path="updated-transactions")
    def updated_transactions(self, request, pk):
        data = self.get_object()

        bank_statements = (
            data.rows.filter(
                statement__company=request.company,
                statement__account_id=data.account_id,
                id__in=data.rows.filter(
                    transactions__transaction_last_updated_at__lt=F('transactions__transaction__updated_at')
                ).values('id')
            )
            .values("id")
            .annotate(
                grouped_statements=ArrayAgg("id", distinct=True),
                transaction_ids=Coalesce(
                    ArrayAgg("transactions__transaction_id", distinct=True), []
                ),
            )
            .order_by("-date")
        )
        
        return self.get_paginated_merged_transactions(bank_statements, request.company, data.account_id)
    
    
    @action(detail=False, methods=['POST'], url_path="update-transactions")
    def update_transactions(self, request):
        statement_ids = request.data.get('statement_ids')
        transaction_ids = request.data.get('transaction_ids')
        if not statement_ids or not transaction_ids:
            raise ValidationError({"detail": "statement_ids and transaction_ids are required"})
        entries = ReconciliationRow.objects.filter(id__in=statement_ids).select_related("statement")
        # Ensure all statement entries belong to the same account_id
        account_ids = {entry.statement.account_id for entry in entries}
        if len(account_ids) > 1:
            raise ValidationError({"detail": "All the statement entries should have the same account_id"})

        # Fetch ReconciliationRowTransaction objects with related transaction
        transaction_objects = ReconciliationRowTransaction.objects.filter(
            reconciliation_row__in=entries,
            transaction_id__in=transaction_ids
        ).select_related("transaction").distinct()


        transaction_objects.update(
            transaction_last_updated_at=Subquery(
                transaction_objects.filter(
                    pk=OuterRef('pk')
                ).values('transaction__updated_at')[:1]
            )
        )

        return Response({})
                


