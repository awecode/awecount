from datetime import date, datetime, timedelta
from itertools import chain, combinations
from django.db import transaction
from django.conf import settings
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
    ChequeDeposit,
    FundTransferTemplate,
    ReconciliationEntries,
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
    ReconciliationEntriesSerializer,
    ReconciliationStatementImportSerializer,
    ReconciliationStatementSerializer,
)
from apps.ledger.models import Account, Party
from apps.ledger.models.base import Transaction
from apps.ledger.serializers import (
    JournalEntriesSerializer,
    PartyMinSerializer,
    TransactionMinSerializer,
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


class ReconciliationViewSet(CRULViewSet):
    queryset = ReconciliationStatement.objects.all()
    serializer_class = ReconciliationStatementSerializer
    model = ReconciliationStatement

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
                    statement_transaction['transaction_ids'] = [system_transaction.pk]
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
            for r in range(1, len(statement_transactions) + 1):
                for combination in combinations(statement_transactions, r):
                    total_dr = sum(t.get('dr_amount', 0) for t in combination)
                    total_cr = sum(t.get('cr_amount', 0) for t in combination)

                    if (
                        abs(total_dr - (system_transaction.cr_amount or 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                        abs(total_cr - (system_transaction.dr_amount or 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                    ):
                        # Reconcile matched transactions
                        for statement_transaction in combination:
                            if statement_transaction.get('transaction_ids'):
                                statement_transaction['transaction_ids'].append(system_transaction.pk)
                            else:
                                statement_transaction['transaction_ids'] = [system_transaction.pk]
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
                for r in range(1, len(system_transactions) + 1):
                    for combination in combinations(system_transactions, r):
                        total_dr = sum((t.dr_amount or 0) for t in combination)
                        total_cr = sum((t.cr_amount or 0) for t in combination)

                        if (
                            abs(total_dr - statement_transaction.get('cr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                            abs(total_cr - statement_transaction.get('dr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                        ):
                            # Reconcile matched transactions
                            for system_transaction in combination:
                                if statement_transaction.get('transaction_ids'):
                                    statement_transaction['transaction_ids'].append(system_transaction.pk)
                                else:
                                    statement_transaction['transaction_ids'] = [system_transaction.pk]
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
                                if statement_transaction.get('transaction_ids'):
                                    statement_transaction['transaction_ids'].append(system_transaction.pk)
                                else:
                                    statement_transaction['transaction_ids'] = [system_transaction.pk]
                                if has_same_date:
                                    statement_transaction['status'] = 'Reconciled'
                                unreconciled_system_transactions.remove(system_transaction)
                                system_transactions_by_date[system_transaction.journal_entry.date.strftime('%Y-%m-%d')].remove(system_transaction)
      
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(statement_transaction)
                            return True
            
            
            for r in range(1, len(system_transactions) + 1):
                for combination in combinations(system_transactions, r):
                    total_dr = sum((t.dr_amount or 0) for t in combination)
                    total_cr = sum((t.cr_amount or 0) for t in combination)

                    if (
                        abs(total_dr - statement_transaction.get('cr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE and
                        abs(total_cr - statement_transaction.get('dr_amount', 0)) < settings.BANK_RECONCILIATION_TOLERANCE
                    ):
                        # Reconcile matched transactions
                        for system_transaction in combination:
                            if statement_transaction.get('transaction_ids'):
                                statement_transaction['transaction_ids'].append(system_transaction.pk)
                            else:
                                statement_transaction['transaction_ids'] = [system_transaction.pk]
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
        for statement_transaction in unreconciled_statement_transactions[:]:
            date_str = statement_transaction['date']
            if date_str in system_transactions_by_date:
                # Filter system transactions by date
                date_filtered_system_transactions = [
                    t for t in unreconciled_system_transactions if t.journal_entry.date.strftime('%Y-%m-%d') == date_str
                ]
                
                # Try different combination lengths to find matching net debit-credit difference
                for r in range(1, len(date_filtered_system_transactions) + 1):
                    for combination in combinations(date_filtered_system_transactions, r):
                        # Calculate the net difference: debits - credits
                        net_difference = sum((t.dr_amount or 0) - (t.cr_amount or 0) for t in combination)
                        
                        # Check if the net difference matches the statement transaction amount
                        if abs(round(net_difference, 2) - round(float(statement_transaction.get('cr_amount', 0)), 2)) < settings.BANK_RECONCILIATION_TOLERANCE:
                            # Mark these transactions as reconciled
                            for system_transaction in combination:
                                if statement_transaction.get('transaction_ids'):
                                    statement_transaction['transaction_ids'].append(system_transaction.pk)
                                else:
                                    statement_transaction['transaction_ids'] = [system_transaction.pk]
                                statement_transaction['status'] = 'Reconciled'
                                
                                # if system_transaction in unreconciled_system_transactions:
                                unreconciled_system_transactions.remove(system_transaction)
                                # if system_transaction in system_transactions_by_date[date_str]:
                                system_transactions_by_date[date_str].remove(system_transaction)

                            # Add to reconciled transactions and remove from the original list
                            reconciled_transactions.append(statement_transaction)
                            unreconciled_statement_transactions.remove(statement_transaction)

                            # Clean up system transactions by date if empty
                            if not system_transactions_by_date[date_str]:
                                del system_transactions_by_date[date_str]

                            break  # Stop after finding a valid combination
                    else:
                        continue  # Only runs if the inner loop is not broken
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
                statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
                date_range_start = statement_date
                date_range_end = statement_date + timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS)

                # Filter system transactions within 3 days of the statement transaction date
                date_filtered_system_transactions = [
                    t for t in unreconciled_system_transactions
                    if date_range_start <= t.journal_entry.date <= date_range_end
                ]

                # Group system transactions by date
                merged_system_transactions_by_date = {}
                for system_transaction in date_filtered_system_transactions:
                    date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
                    merged_system_transactions_by_date.setdefault(date_str, []).append(system_transaction)

                # Loop over the grouped transactions and try to reconcile
                for date_str, system_transactions_by_date in list(merged_system_transactions_by_date.items()):
                    for r in range(1, len(system_transactions_by_date) + 1):
                        for combination in combinations(system_transactions_by_date, r):
                            # Calculate the net difference: debits - credits
                            net_difference = sum((t.dr_amount or 0) - (t.cr_amount or 0) for t in combination)

                            # Check if the net difference matches the statement transaction amount
                            if abs(round(net_difference, 2) - round(float(statement_transaction.get('cr_amount', 0)), 2)) < settings.BANK_RECONCILIATION_TOLERANCE:
                                # Mark these transactions as reconciled
                                for system_transaction in combination:
                                    statement_transaction.setdefault('transaction_ids', []).append(system_transaction.pk)
                                    if system_transaction in unreconciled_system_transactions:
                                        unreconciled_system_transactions.remove(system_transaction)

                                # Add to reconciled transactions and remove from the original list
                                reconciled_transactions.append(statement_transaction)
                                if statement_transaction in unreconciled_statement_transactions:
                                    unreconciled_statement_transactions.remove(statement_transaction)

                                # Clean up system transactions by date if empty
                                merged_system_transactions_by_date[date_str] = [
                                    t for t in merged_system_transactions_by_date[date_str] if t not in combination
                                ]
                                if not merged_system_transactions_by_date[date_str]:
                                    del merged_system_transactions_by_date[date_str]

                                break  # Stop after finding a valid combination
                        else:
                            continue  # Only runs if the inner loop is not broken
                        break  # Exit the loop if a match is found
        
        
        
        # now compare the remaining unreconciled statement transactions and unreconciled system transactions, where system_transaction date can be within 3 days of statement_transaction date
        
        for statement_transaction in unreconciled_statement_transactions[:]:
                statement_date = datetime.strptime(statement_transaction['date'], '%Y-%m-%d').date()
                date_range_start = statement_date - timedelta(days=settings.BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS)
                date_range_end = statement_date

                # Filter system transactions within 3 days of the statement transaction date
                date_filtered_system_transactions = [
                    t for t in unreconciled_system_transactions
                    if date_range_start <= t.journal_entry.date <= date_range_end
                ]

                # Group system transactions by date
                merged_system_transactions_by_date = {}
                for system_transaction in date_filtered_system_transactions:
                    date_str = system_transaction.journal_entry.date.strftime('%Y-%m-%d')
                    merged_system_transactions_by_date.setdefault(date_str, []).append(system_transaction)

                # Loop over the grouped transactions and try to reconcile
                for date_str, system_transactions_by_date in list(merged_system_transactions_by_date.items()):
                    for r in range(1, len(system_transactions_by_date) + 1):
                        for combination in combinations(system_transactions_by_date, r):
                            # Calculate the net difference: debits - credits
                            net_difference = sum((t.dr_amount or 0) - (t.cr_amount or 0) for t in combination)

                            # Check if the net difference matches the statement transaction amount
                            if abs(round(net_difference, 2) - round(float(statement_transaction.get('cr_amount', 0)), 2)) < settings.BANK_RECONCILIATION_TOLERANCE:
                                # Mark these transactions as reconciled
                                for system_transaction in combination:
                                    statement_transaction.setdefault('transaction_ids', []).append(system_transaction.pk)
                                    if system_transaction in unreconciled_system_transactions:
                                        unreconciled_system_transactions.remove(system_transaction)

                                # Add to reconciled transactions and remove from the original list
                                reconciled_transactions.append(statement_transaction)
                                if statement_transaction in unreconciled_statement_transactions:
                                    unreconciled_statement_transactions.remove(statement_transaction)

                                # Clean up system transactions by date if empty
                                merged_system_transactions_by_date[date_str] = [
                                    t for t in merged_system_transactions_by_date[date_str] if t not in combination
                                ]
                                if not merged_system_transactions_by_date[date_str]:
                                    del merged_system_transactions_by_date[date_str]

                                break  # Stop after finding a valid combination
                        else:
                            continue  # Only runs if the inner loop is not broken
                        break  # Exit the loop if a match is found

        # Combine reconciled and unreconciled transactions into a single list
        bank_reconciliation_entries = []
        
        # add to bank reconciliation
        bank_reconciliation_statement = ReconciliationStatement.objects.create(
            company=company,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
        ) 

        # Add reconciled transactions
        for statement_transaction in reconciled_transactions:
            bank_reconciliation_entries.append(ReconciliationEntries(
                date=statement_transaction['date'],
                dr_amount=statement_transaction.get('dr_amount', None),
                cr_amount=statement_transaction.get('cr_amount', None),
                status=statement_transaction.get('status', 'Matched'),
                balance=statement_transaction.get('balance', None),
                transaction_ids=statement_transaction.get('transaction_ids', []),
                statement_id=bank_reconciliation_statement.pk,
                description=statement_transaction.get('description', None),
            ))

        # Add unreconciled transactions
        for statement_transaction in unreconciled_statement_transactions:
            bank_reconciliation_entries.append(ReconciliationEntries(
                date=statement_transaction['date'],
                dr_amount=statement_transaction.get('dr_amount', None),
                cr_amount=statement_transaction.get('cr_amount', None),
                status='Unreconciled',
                balance=statement_transaction.get('balance', None),
                statement_id=bank_reconciliation_statement.pk,
                description=statement_transaction.get('description', None),
            ))

        # Perform bulk_create once
        ReconciliationEntries.objects.bulk_create(bank_reconciliation_entries,  batch_size=500)
                            
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
        
        # TODO: throw in background task
        response = self.reconcile(request.company, transactions, start_date, end_date, account_id)
        return Response(response)
    
    
    @action(detail=False, url_path="unreconciled-transactions")
    def unreconciled_transactions(self, request):
        # get start_date and end_date from request
        # also get account_id
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        account_id = request.query_params.get('account_id')
        
        if not start_date or not end_date or not account_id:
            raise APIException("start_date, end_date and account_id are required")

        # Fetch reconciled transaction IDs for the same company, account, and date
        reconciled_transaction_ids = ReconciliationEntries.objects.filter(
            statement__company=request.company,
            statement__account_id=account_id,
            date__range=[start_date, end_date],
            status='Reconciled'
        ).values_list('transaction_ids', flat=True)

        reconciled_transaction_ids_set = set(chain.from_iterable(reconciled_transaction_ids))

        transactions = Transaction.objects.filter(
            company=request.company,
            journal_entry__date__range=[start_date, end_date],
            account_id=account_id
        ).exclude(
            id__in=reconciled_transaction_ids_set
        ).order_by("journal_entry__date").select_related("journal_entry__content_type").prefetch_related(
            "journal_entry__transactions__account",
            "journal_entry__source"
        )

        # fetch bank reconciliation entries
        bank_statements = ReconciliationEntries.objects.filter(
            statement__company=request.company, statement__account_id=account_id, date__range=[start_date, end_date],
            status__in=['Unreconciled', 'Matched']
        ).order_by("date")
        
        return Response({ 'system_transactions': TransactionMinSerializer(transactions, many=True).data, 'statement_transactions': ReconciliationEntriesSerializer(bank_statements, many=True).data, 'acceptable_difference':  settings.BANK_RECONCILIATION_TOLERANCE })
    
    @action(detail=False, methods=["POST"], url_path="reconcile-transactions")
    def reconcile_transactions(self, request):
        statement_ids = request.data.get('statement_ids')
        transaction_ids = request.data.get('transaction_ids')
        if not statement_ids or not transaction_ids:
            raise APIException("statement_ids and transaction_ids are required")
        statement_objects = ReconciliationEntries.objects.filter(id__in=statement_ids)
        transaction_objects = Transaction.objects.filter(id__in=transaction_ids)
        statement_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in statement_objects])
        transaction_sum = sum([obj.dr_amount - (obj.cr_amount or 0) if obj.dr_amount else -obj.cr_amount for obj in transaction_objects])
        if abs(statement_sum - transaction_sum) > settings.BANK_RECONCILIATION_TOLERANCE:
            raise APIException("The sum of the statement transactions and system transactions do not match")
        statement_objects.update(status='Reconciled', transaction_ids=transaction_ids)
        return Response({})

    @action(detail=False, methods=["POST"], url_path="unmatch-transactions")
    def unmatch_transactions(self, request):
        statement_ids = request.data.get('statement_ids')
        if not statement_ids:
            raise APIException("statement_ids are required")
        statement_objects = ReconciliationEntries.objects.filter(id__in=statement_ids)
        statement_objects.update(status='Unreconciled', transaction_ids=[])
        return Response({})
    
    @action(detail=False, methods=["POST"], url_path="reconcile-with-adjustment")
    def reconcile_with_adjustment(self, request):
        statement_ids = request.data.get('statement_ids')
        transaction_ids = request.data.get('transaction_ids')
        narration = request.data.get('narration')
        # TODO: max number of statement_ids
        if not statement_ids or not transaction_ids or not narration or len(statement_ids) > 10:
            raise APIException("statement_ids, transaction_ids and narration are required")
        statement_objects = ReconciliationEntries.objects.filter(id__in=statement_ids)
        transaction_objects = Transaction.objects.filter(id__in=transaction_ids).select_related("journal_entry")
        statement_sum = sum([obj.cr_amount - (obj.dr_amount or 0) if obj.cr_amount else -obj.dr_amount for obj in statement_objects])
        transaction_sum = sum([obj.dr_amount - (obj.cr_amount or 0) if obj.dr_amount else -obj.cr_amount for obj in transaction_objects])
        # find the difference
        difference = statement_sum - transaction_sum
        # Divide the difference by the number of statement transactions and put the difference in the adjustment field
        # date = get latest date of the system from transaction_objects
        latest_date = max(
            (obj.journal_entry.date for obj in transaction_objects if obj.journal_entry and obj.journal_entry.date),
            default=date.min 
        )
        adjustment = abs(difference) / len(statement_objects)
        with transaction.atomic():
            for obj in statement_objects:
                obj.transaction_ids = transaction_ids
                obj.adjustment_amount = adjustment
                obj.adjustment_type = 'Cr' if difference > 0 else 'Dr'
                obj.save()
                obj.status = 'Matched'
                obj.apply_transactions(latest_date)
        return Response({})
        

