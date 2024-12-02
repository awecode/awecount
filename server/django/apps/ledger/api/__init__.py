from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, F, FloatField, Max, Q, Sum, When
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from mptt.utils import get_cached_trees
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.aggregator.views import qs_to_xls
from apps.ledger.filters import AccountFilterSet, CategoryFilterSet
from apps.ledger.models.base import AccountClosing, Transaction
from apps.ledger.resources import TransactionGroupResource, TransactionResource
from apps.tax.models import TaxScheme
from apps.users.models import FiscalYear
from apps.voucher.models import PurchaseVoucher, SalesVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from awecount.libs.CustomViewSet import (
    CollectionViewSet,
    CompanyViewSetMixin,
    CRULViewSet,
    GenericSerializer,
)
from awecount.libs.mixins import InputChoiceMixin, TransactionsViewMixin

from ..models import Account, AccountOpeningBalance, Category, JournalEntry
from ..serializers import (
    AccountClosingSerializer,
    AccountDetailSerializer,
    AccountFormSerializer,
    AccountListSerializer,
    AccountOpeningBalanceListSerializer,
    AccountOpeningBalanceSerializer,
    AccountSerializer,
    AggregatorSerializer,
    CategoryDetailSerializer,
    CategorySerializer,
    CategoryTreeSerializer,
    ContentTypeListSerializer,
    JournalEntrySerializer,
    PartyAccountSerializer,
    PartyListSerializer,
    PartyMinSerializer,
    PartySerializer,
    TransactionReportSerializer,
)


class PartyViewSet(
    InputChoiceMixin, TransactionsViewMixin, DestroyModelMixin, CRULViewSet
):
    serializer_class = PartySerializer
    account_keys = ["supplier_account", "customer_account"]
    choice_serializer_class = PartyMinSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    )
    search_fields = (
        "name",
        "tax_registration_number",
        "contact_no",
        "address",
    )

    def get_account_ids(self, obj):
        return [obj.supplier_account_id, obj.customer_account_id]

    def get_serializer_class(self):
        if self.action == "transactions":
            return PartyAccountSerializer
        if self.action in ["list", "customers", "suppliers"]:
            return PartyListSerializer
        return PartySerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by("-pk")
        if self.action == "transactions":
            qs = qs.select_related("supplier_account", "customer_account")
        if self.action == "customers":
            qs = (
                qs.filter(customer_account__transactions__isnull=False)
                .annotate(
                    dr=Coalesce(Sum("customer_account__transactions__dr_amount"), 0.0),
                    cr=Coalesce(Sum("customer_account__transactions__cr_amount"), 0.0),
                )
                .annotate(balance=F("dr") - F("cr"))
            )
        if self.action == "suppliers":
            qs = (
                qs.filter(supplier_account__transactions__isnull=False)
                .annotate(
                    dr=Coalesce(Sum("supplier_account__transactions__dr_amount"), 0.0),
                    cr=Coalesce(Sum("supplier_account__transactions__cr_amount"), 0.0),
                )
                .annotate(balance=F("dr") - F("cr"))
            )
        return qs

    @action(detail=True)
    def sales_vouchers(self, request, pk=None):
        sales_vouchers = SalesVoucher.objects.filter(party_id=pk)
        data = SaleVoucherOptionsSerializer(sales_vouchers, many=True).data
        return Response(data)

    @action(detail=False)
    def customers(self, request):
        return super().list(request)

    @action(detail=False)
    def suppliers(self, request):
        return super().list(request)


class CategoryViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = CategorySerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    )
    search_fields = ("code", "name")
    filterset_class = CategoryFilterSet

    collections = (
        ("categories", Category, CategorySerializer, True, ["code", "name"]),
    )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return super().get_serializer_class()


class AccountViewSet(InputChoiceMixin, TransactionsViewMixin, CRULViewSet):
    serializer_class = AccountSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    )
    search_fields = ("code", "name")
    filterset_class = AccountFilterSet

    def get_account_ids(self, obj):
        return [obj.id]

    def get_queryset(self):
        qs = Account.objects.filter(company=self.request.company).select_related(
            "category", "parent"
        )
        # if self.action == "list":
        #     qs = (
        #         qs.annotate(
        #             dr=Coalesce(Sum("transactions__dr_amount"), 0.0),
        #             cr=Coalesce(Sum("transactions__cr_amount"), 0.0),
        #         )
        #         .annotate(computed_balance=F("dr") - F("cr"))
        #         .order_by("-id")
        #     )
        return qs

    def get_accounts_by_category_name(self, category_name):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            category__name=category_name, company=self.request.company
        )
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    def get_serializer_class(self):
        if self.action == "transactions":
            return AccountDetailSerializer
        if self.action in ["create", "update"]:
            return AccountFormSerializer
        if self.action in ["list"]:
            return AccountListSerializer
        return AccountSerializer

    @action(detail=True, methods=["get"], url_path="journal-entries")
    def journal_entries(self, request, pk=None):
        param = request.GET
        start_date = param.get("start_date")
        end_date = param.get("end_date")
        obj = self.get_object()
        entries = (
            JournalEntry.objects.filter(transactions__account_id=obj.pk)
            .order_by("pk", "date")
            .prefetch_related("transactions", "content_type", "transactions__account")
            .select_related()
        )

        if start_date or end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            if start_date == end_date:
                entries = entries.filter(date=start_date)
            else:
                entries = entries.filter(date__range=[start_date, end_date])
        data = JournalEntrySerializer(entries, context={"account": obj}, many=True).data
        return Response(data)


class CategoryTreeView(APIView):
    action = "list"

    def get_queryset(self):
        return Category.objects.exclude(
            Q(accounts__isnull=True) & Q(children__isnull=True)
        )

    def get(self, request, format=None):
        queryset = self.get_queryset().filter(company=request.company)
        category_tree = get_cached_trees(queryset)
        serializer = CategoryTreeSerializer(category_tree, many=True)
        return Response(serializer.data)


class FullCategoryTreeView(APIView):
    action = "list"

    def get_queryset(self):
        return Category.objects.all()

    def get(self, request, format=None):
        queryset = self.get_queryset().filter(company=request.company)
        category_tree = get_cached_trees(queryset)
        serializer = CategoryTreeSerializer(category_tree, many=True)
        return Response(serializer.data)


class TrialBalanceView(APIView):
    action = "list"

    def get_queryset(self):
        return Account.objects.none()

    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if start_date and end_date:
            # TODO Only use Transactions whose journal_entry.type=='Regular'
            qq = (
                Account.objects.filter(company=request.company)
                .annotate(
                    od=Sum(
                        "transactions__dr_amount",
                        filter=Q(transactions__journal_entry__date__lt=start_date),
                    ),
                    oc=Sum(
                        "transactions__cr_amount",
                        filter=Q(transactions__journal_entry__date__lt=start_date),
                    ),
                    cd=Sum(
                        "transactions__dr_amount",
                        filter=Q(transactions__journal_entry__date__lt=end_date)
                        | Q(
                            transactions__journal_entry__date=end_date,
                            transactions__type="Regular",
                        ),
                    ),
                    cc=Sum(
                        "transactions__cr_amount",
                        filter=Q(transactions__journal_entry__date__lt=end_date)
                        | Q(
                            transactions__journal_entry__date=end_date,
                            transactions__type="Regular",
                        ),
                    ),
                )
                .values("id", "name", "category_id", "od", "oc", "cd", "cc")
                .exclude(od=None, oc=None, cd=None, cc=None)
            )
            return Response(list(qq))
        return Response({})


class TaxSummaryView(APIView):
    action = "list"

    def get_queryset(self):
        return TaxScheme.objects.none()

    def get_sales_queryset(self, **kwargs):
        return SalesVoucher.objects.filter(
            company_id=self.request.company_id,
            status__in=["Issued", "Paid", "Partially Paid"],
        )

    def get_non_import_purchase_queryset(self, **kwargs):
        return (
            PurchaseVoucher.objects.filter(is_import=False)
            .filter(Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0))
            .filter(
                company_id=self.request.company_id,
                status__in=["Issued", "Paid", "Partially Paid"],
            )
            .distinct()
        )

    def get_import_purchase_queryset(self, **kwargs):
        return (
            PurchaseVoucher.objects.filter(is_import=True)
            .filter(Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0))
            .filter(
                company_id=self.request.company_id,
                status__in=["Issued", "Paid", "Partially Paid"],
            )
            .distinct()
        )

    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not (start_date and end_date):
            raise ValidationError("Start and end dates are required.")

        sales_data = (
            self.get_sales_queryset()
            .filter(date__gte=start_date, date__lte=end_date)
            .aggregate(
                total_meta_tax=Sum("meta_tax"),
                total_meta_taxable=Sum("meta_taxable"),
                total_meta_non_taxable=Sum("meta_non_taxable"),
                total_export=Sum(Case(When(is_export=True, then=F("total_amount")))),
            )
        )

        non_import_purchase_data = (
            self.get_non_import_purchase_queryset()
            .filter(date__gte=start_date, date__lte=end_date)
            .aggregate(
                total_meta_tax=Sum("meta_tax"),
                total_meta_taxable=Sum("meta_taxable"),
                total_meta_non_taxable=Sum("meta_non_taxable"),
            )
        )

        import_purchase_data = (
            self.get_import_purchase_queryset()
            .filter(date__gte=start_date, date__lte=end_date)
            .aggregate(
                total_meta_tax=Sum("meta_tax"),
                total_meta_taxable=Sum("meta_taxable"),
                total_meta_non_taxable=Sum("meta_non_taxable"),
            )
        )

        return Response(
            {
                "sales": sales_data,
                "purchase": non_import_purchase_data,
                "import": import_purchase_data,
            }
        )


class AccountOpeningBalanceViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = AccountOpeningBalanceSerializer

    filter_backends = (
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    )
    search_fields = ("account__name", "opening_dr", "opening_cr")

    def get_serializer_class(self):
        if self.action == "list":
            return AccountOpeningBalanceListSerializer
        return self.serializer_class

    def get_queryset(self):
        return AccountOpeningBalance.objects.filter(
            fiscal_year=self.request.company.current_fiscal_year,
            company=self.request.company,
        ).order_by("-pk")

    collections = (
        (
            "accounts",
            Account.objects.exclude(name__startswith="Opening Balance").filter(
                account_opening_balances__isnull=True
            ),
            GenericSerializer,
            True,
            ["name"],
        ),
    )


class CustomerClosingView(APIView):
    action = "list"

    def get_queryset(self):
        return Account.objects.filter(customer_detail__isnull=False)

    def get(self, request, format=None):
        customers = (
            self.get_queryset()
            .filter(company_id=self.request.user.company_id)
            .exclude(transactions__isnull=True)
        )

        balances = customers.annotate(
            dr=Sum("transactions__dr_amount"),
            cr=Sum("transactions__cr_amount"),
        ).values("dr", "cr", "customer_detail__tax_registration_number", "id")

        last_invoice_dates = customers.annotate(
            last_invoice_date=Max(
                Case(
                    When(
                        customer_detail__sales_invoices__status__in=[
                            "Issued",
                            "Paid",
                            "Partially Paid",
                        ],
                        then="customer_detail__sales_invoices__date",
                    )
                )
            )
        ).values("customer_detail__tax_registration_number", "id", "last_invoice_date")
        return Response(
            {"balances": balances, "last_invoice_dates": last_invoice_dates}
        )


class TransactionViewSet(
    CompanyViewSetMixin, CollectionViewSet, ListModelMixin, GenericViewSet
):
    company_id_attr = "journal_entry__company_id"
    serializer_class = TransactionReportSerializer
    filter_backends = [DjangoFilterBackend, rf_filters.SearchFilter]
    # filterset_class = TransactionFilterSet
    search_fields = ["account__name", "account__category__name"]
    exculde_content_type_models = ["salesvoucher", "purchasevoucher", "creditnote", "debitnote"]
    journal_entry_content_type = JournalEntry.objects.values_list(
        "content_type", flat=True
    ).distinct()
    collections = [
        ("accounts", Account, GenericSerializer, True, ["name"]),
        (
            "transaction_types",
            ContentType.objects.filter(id__in=journal_entry_content_type).exclude(
                model__in=exculde_content_type_models
            ),
            ContentTypeListSerializer,
            True,
            ["app_label"],
        ),
        (
            "categories",
            Category,
            GenericSerializer,
            True,
            ["name"],
        ),
    ]

    def get_serializer_class(self):
        if self.request.GET.get("group"):
            return AggregatorSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = (
            Transaction.objects.filter(company_id=self.request.company_id)
            .prefetch_related("account", "journal_entry__content_type")
            .order_by("-journal_entry__date")
        )
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        accounts = list(filter(None, self.request.GET.getlist("account")))
        categories = list(filter(None, self.request.GET.getlist("category")))
        sources = list(filter(None, self.request.GET.getlist("source")))
        group_by = self.request.GET.get("group")

        # TODO Optimize this query
        if start_date and end_date:
            qs = qs.filter(journal_entry__date__range=[start_date, end_date])
        if accounts:
            qs = qs.filter(account_id__in=accounts)
        if categories:
            qs = qs.filter(account__category_id__in=categories)
        if sources:
            qs = qs.filter(journal_entry__content_type_id__in=sources)
        if group_by:
            qs = self.aggregate(qs, group_by)
        return qs

    def aggregate(self, qs, group_by):
        from django.db.models import Sum
        from django.db.models.functions import ExtractYear

        if group_by == "acc":
            qs = (
                qs.annotate(
                    year=ExtractYear("journal_entry__date"), label=F("account__name")
                )
                .values("year", "label")
                .annotate(
                    total_debit=Sum("dr_amount"),
                    total_credit=Sum("cr_amount"),
                )
                .order_by("-year")
            )
        if group_by == "cat":
            qs = (
                qs.annotate(
                    year=ExtractYear("journal_entry__date"),
                    label=F("account__category__name"),
                )
                .values("year", "label")
                .annotate(
                    total_debit=Sum("dr_amount"),
                    total_credit=Sum("cr_amount"),
                )
                .order_by("-year")
            )
        if group_by == "type":
            qs = (
                qs.annotate(
                    year=ExtractYear("journal_entry__date"),
                    label=F("journal_entry__content_type__model"),
                )
                .values("year", "label")
                .annotate(
                    total_debit=Sum("dr_amount"),
                    total_credit=Sum("cr_amount"),
                )
                .order_by("-year")
            )
        return qs

    @action(detail=False)
    def export(self, request):
        queryset = self.get_queryset().order_by("-journal_entry__date")
        if not request.GET.get("group"):
            params = [("Transactions", queryset, TransactionResource)]
            return qs_to_xls(params)
        else:
            params = [("Transactions", queryset, TransactionGroupResource)]
            return qs_to_xls(params)

    @action(detail=False, url_path="day-book")
    def day_book(self, request):
        date_str = self.request.GET.get("date") or datetime.now().date().isoformat()
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

        combined_accounts = (
            Account.objects.filter(company=request.company)
            .annotate(
                today_dr=Coalesce(
                    Sum(
                        Case(
                            When(
                                transactions__journal_entry__date=target_date,
                                then="transactions__dr_amount",
                            ),
                            default=0.0,
                            output_field=FloatField(),
                        )
                    ),
                    0.0,
                ),
                today_cr=Coalesce(
                    Sum(
                        Case(
                            When(
                                transactions__journal_entry__date=target_date,
                                then="transactions__cr_amount",
                            ),
                            default=0.0,
                            output_field=FloatField(),
                        )
                    ),
                    0.0,
                ),
                total_dr=Coalesce(
                    Sum(
                        Case(
                            When(
                                transactions__journal_entry__date__lte=target_date,
                                then="transactions__dr_amount",
                            ),
                            default=0.0,
                            output_field=FloatField(),
                        )
                    ),
                    0.0,
                ),
                total_cr=Coalesce(
                    Sum(
                        Case(
                            When(
                                transactions__journal_entry__date__lte=target_date,
                                then="transactions__cr_amount",
                            ),
                            default=0.0,
                            output_field=FloatField(),
                        )
                    ),
                    0.0,
                ),
            )
            .filter(
                Case(
                    When(
                        category__name__in=["Cash Accounts", "Bank Accounts"],
                        then=True,
                    ),
                    When(transactions__journal_entry__date=target_date, then=True),
                    default=False,
                )
            )
            .distinct()
        )

        account_transactions = [
            {
                "account": {
                    "id": account.id,
                    "name": account.name,
                    "code": account.code,
                },
                "has_transactions": account.today_dr - account.today_cr != 0,
                "opening_balance": account.total_dr
                - account.total_cr
                - (account.today_dr - account.today_cr),
                "closing_balance": account.total_dr - account.total_cr,
            }
            for account in combined_accounts
        ]

        return Response(account_transactions)


class AccountClosingViewSet(
    CollectionViewSet, ListModelMixin, CreateModelMixin, GenericViewSet
):
    queryset = AccountClosing.objects.all()
    serializer_class = AccountClosingSerializer

    collections = [("fiscal_years", FiscalYear, GenericSerializer, True, ["name"])]

    def get_defaults(self, request=None):
        company = request.company
        current_fiscal_year = GenericSerializer(company.current_fiscal_year).data
        return {"fields": {"current_fiscal_year": current_fiscal_year}}

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.company)

    def create(self, request, *args, **kwargs):
        company = request.company
        fiscal_year_id = request.data.get("fiscal_year")
        account_closing = AccountClosing.objects.get_or_create(
            company=company, fiscal_period_id=fiscal_year_id
        )[0]
        if account_closing.status == "Closed":
            return Response(
                {"detail": "Your accounts for this year have already been closed."},
                status=400,
            )
        account_closing.close()
        return Response(
            "Successfully closed accounts for selected fiscal year.", status=200
        )
