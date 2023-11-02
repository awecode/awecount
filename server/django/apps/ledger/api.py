from datetime import datetime

from django.db.models import Q, Sum, Case, When, F, Max
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from django_filters import rest_framework as filters
from mptt.utils import get_cached_trees
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from apps.aggregator.views import qs_to_xls

from apps.ledger.filters import AccountFilterSet, CategoryFilterSet, TransactionFilterSet
from apps.ledger.models.base import AccountClosing
from apps.ledger.resources import TransactionGroupResource, TransactionResource
from apps.tax.models import TaxScheme
from apps.users.models import FiscalYear
from apps.voucher.models import SalesVoucher, PurchaseVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from awecount.libs.CustomViewSet import CRULViewSet, CollectionViewSet, CompanyViewSetMixin
from awecount.libs.mixins import InputChoiceMixin, TransactionsViewMixin
from .models import Account, JournalEntry, Category, AccountOpeningBalance
from .serializers import AccountClosingSerializer, AggregatorSerializer, ContentTypeListSerializer, PartySerializer, AccountSerializer, \
    AccountDetailSerializer, CategorySerializer, \
    JournalEntrySerializer, \
    PartyMinSerializer, PartyAccountSerializer, CategoryTreeSerializer, AccountOpeningBalanceSerializer, \
    AccountOpeningBalanceListSerializer, AccountFormSerializer, PartyListSerializer, AccountListSerializer, \
    TransactionEntrySerializer, TransactionReportSerializer


class PartyViewSet(InputChoiceMixin, TransactionsViewMixin, DestroyModelMixin, CRULViewSet):
    serializer_class = PartySerializer
    account_keys = ['supplier_account', 'customer_account']
    choice_serializer_class = PartyMinSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('name', 'tax_registration_number', 'contact_no', 'address',)

    def get_account_ids(self, obj):
        return [obj.supplier_account_id, obj.customer_account_id]

    def get_serializer_class(self):
        if self.action == 'transactions':
            return PartyAccountSerializer
        if self.action in ['list', 'customers', 'suppliers']:
            return PartyListSerializer
        return PartySerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-pk')
        if self.action == 'transactions':
            qs = qs.select_related('supplier_account', 'customer_account')
        if self.action == 'customers':
            qs = qs.filter(customer_account__transactions__isnull=False).annotate(
                dr=Coalesce(Sum('customer_account__transactions__dr_amount'), 0.0),
                cr=Coalesce(Sum('customer_account__transactions__cr_amount'), 0.0)).annotate(
                balance=F('dr') - F('cr'))
        if self.action == 'suppliers':
            qs = qs.filter(supplier_account__transactions__isnull=False).annotate(
                dr=Coalesce(Sum('supplier_account__transactions__dr_amount'), 0.0),
                cr=Coalesce(Sum('supplier_account__transactions__cr_amount'), 0.0)).annotate(
                balance=F('dr') - F('cr'))
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
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)
    filterset_class = CategoryFilterSet

    collections = (
        ('categories', Category, CategorySerializer),
    )


class AccountViewSet(InputChoiceMixin, TransactionsViewMixin, CRULViewSet):
    serializer_class = AccountSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)
    filterset_class = AccountFilterSet

    def get_account_ids(self, obj):
        return [obj.id]

    def get_queryset(self):
        qs = Account.objects.filter(company=self.request.company).select_related('category', 'parent')
        if self.action == 'list':
            qs = qs.annotate(
                dr=Coalesce(Sum('transactions__dr_amount'), 0.0),
                cr=Coalesce(Sum('transactions__cr_amount'), 0.0)).annotate(
                computed_balance=F('dr') - F('cr'))
        return qs

    def get_accounts_by_category_name(self, category_name):
        queryset = self.get_queryset()
        queryset = queryset.filter(category__name=category_name, company=self.request.company)
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    def get_serializer_class(self):
        if self.action == 'transactions':
            return AccountDetailSerializer
        if self.action in ['create', 'update']:
            return AccountFormSerializer
        if self.action in ['list']:
            return AccountListSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'], url_path='journal-entries')
    def journal_entries(self, request, pk=None):
        param = request.GET
        start_date = param.get('start_date')
        end_date = param.get('end_date')
        obj = self.get_object()
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()

        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if start_date == end_date:
                entries = entries.filter(date=start_date)
            else:
                entries = entries.filter(date__range=[start_date, end_date])
        data = JournalEntrySerializer(entries, context={'account': obj}, many=True).data
        return Response(data)


class CategoryTreeView(APIView):
    action = 'list'

    def get_queryset(self):
        return Category.objects.exclude(Q(accounts__isnull=True) & Q(children__isnull=True))

    def get(self, request, format=None):
        queryset = self.get_queryset().filter(company=request.company)
        category_tree = get_cached_trees(queryset)
        serializer = CategoryTreeSerializer(category_tree, many=True)
        return Response(serializer.data)


class FullCategoryTreeView(APIView):
    action = 'list'

    def get_queryset(self):
        return Category.objects.all()

    def get(self, request, format=None):
        queryset = self.get_queryset().filter(company=request.company)
        category_tree = get_cached_trees(queryset)
        serializer = CategoryTreeSerializer(category_tree, many=True)
        return Response(serializer.data)


class TrialBalanceView(APIView):
    action = 'list'

    def get_queryset(self):
        return Account.objects.none()

    def get(self, request, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            # TODO Only use Transactions whose journal_entry.type=='Regular'
            qq = Account.objects.filter(company=request.company).annotate(
                od=Sum('transactions__dr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                oc=Sum('transactions__cr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                cd=Sum('transactions__dr_amount',
                       filter=Q(transactions__journal_entry__date__lt=end_date) | Q(
                           transactions__journal_entry__date=end_date, transactions__type='Regular')),
                cc=Sum('transactions__cr_amount',
                       filter=Q(transactions__journal_entry__date__lt=end_date) | Q(
                           transactions__journal_entry__date=end_date, transactions__type='Regular')),
            ) \
                .values('id', 'name', 'category_id', 'od', 'oc', 'cd', 'cc').exclude(od=None, oc=None, cd=None, cc=None)
            return Response(list(qq))
        return Response({})


class TaxSummaryView(APIView):
    action = 'list'

    def get_queryset(self):
        return TaxScheme.objects.none()

    def get_sales_queryset(self, **kwargs):
        return SalesVoucher.objects.filter(company_id=self.request.company_id,
                                           status__in=['Issued', 'Paid', 'Partially Paid'])

    def get_non_import_purchase_queryset(self, **kwargs):
        return PurchaseVoucher.objects.filter(is_import=False).filter(
            Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0)).filter(
            company_id=self.request.company_id, status__in=['Issued', 'Paid', 'Partially Paid']).distinct()

    def get_import_purchase_queryset(self, **kwargs):
        return PurchaseVoucher.objects.filter(is_import=True).filter(
            Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0)).filter(
            company_id=self.request.company_id, status__in=['Issued', 'Paid', 'Partially Paid']).distinct()

    def get(self, request, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not (start_date and end_date):
            raise ValidationError('Start and end dates are required.')

        sales_data = self.get_sales_queryset().filter(date__gte=start_date, date__lte=end_date).aggregate(
            total_meta_tax=Sum('meta_tax'),
            total_meta_taxable=Sum('meta_taxable'), total_meta_non_taxable=Sum('meta_non_taxable'),
            total_export=Sum(Case(When(is_export=True, then=F('total_amount'))))
        )

        non_import_purchase_data = self.get_non_import_purchase_queryset().filter(date__gte=start_date,
                                                                                  date__lte=end_date).aggregate(
            total_meta_tax=Sum('meta_tax'),
            total_meta_taxable=Sum('meta_taxable'), total_meta_non_taxable=Sum('meta_non_taxable'),
        )

        import_purchase_data = self.get_import_purchase_queryset().filter(date__gte=start_date,
                                                                          date__lte=end_date).aggregate(
            total_meta_tax=Sum('meta_tax'),
            total_meta_taxable=Sum('meta_taxable'), total_meta_non_taxable=Sum('meta_non_taxable'),
        )

        return Response({
            'sales': sales_data,
            'purchase': non_import_purchase_data,
            'import': import_purchase_data,
        })


class AccountOpeningBalanceViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = AccountOpeningBalanceSerializer

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('account__name', 'opening_dr', 'opening_cr')

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountOpeningBalanceListSerializer
        return self.serializer_class

    def get_queryset(self):
        return AccountOpeningBalance.objects.filter(
            fiscal_year=self.request.company.current_fiscal_year, company=self.request.company).order_by('-pk')

    collections = (
        ('accounts', Account.objects.exclude(name__startswith='Opening Balance')),
    )


class CustomerClosingView(APIView):
    action = 'list'

    def get_queryset(self):
        return Account.objects.filter(customer_detail__isnull=False)

    def get(self, request, format=None):
        customers = self.get_queryset().filter(company_id=self.request.user.company_id).exclude(
            transactions__isnull=True)

        balances = customers.annotate(dr=Sum('transactions__dr_amount'), cr=Sum('transactions__cr_amount'), ).values(
            'dr', 'cr', 'customer_detail__tax_registration_number', 'id')

        last_invoice_dates = customers.annotate(last_invoice_date=Max(Case(
            When(customer_detail__sales_invoices__status__in=['Issued', 'Paid', 'Partially Paid'],
                 then='customer_detail__sales_invoices__date')))).values('customer_detail__tax_registration_number',
                                                                         'id',
                                                                         'last_invoice_date')
        return Response({'balances': balances, 'last_invoice_dates': last_invoice_dates})


class TransactionViewSet(CompanyViewSetMixin, CollectionViewSet, ListModelMixin, GenericViewSet):
    company_id_attr = 'journal_entry__company_id'
    serializer_class = TransactionReportSerializer
    filter_backends = [DjangoFilterBackend, rf_filters.SearchFilter]
    # filterset_class = TransactionFilterSet
    search_fields = ['account__name', 'account__category__name']
    journal_entry_content_type = JournalEntry.objects.values_list('content_type', flat=True).distinct()
    collections = [
        ('accounts', Account),
        ('transaction_types', ContentType.objects.filter(id__in=journal_entry_content_type), ContentTypeListSerializer),
        ('categories', Category)
    ]

    def get_serializer_class(self):
        if self.request.GET.get('group'):
            return AggregatorSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('account', 'journal_entry__content_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        accounts = list(filter(None, self.request.GET.getlist('account')))
        categories = list(filter(None, self.request.GET.getlist('category')))
        sources = list(filter(None, self.request.GET.getlist('source')))
        group_by = self.request.GET.get('group')

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
        from django.db.models.functions import ExtractYear
        from django.db.models import Sum

        if group_by == 'acc':
            qs = qs.annotate(year=ExtractYear('journal_entry__date'), label=F('account__name')).values('year',
                                                                                                       'label').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')
        if group_by == 'cat':
            qs = qs.annotate(year=ExtractYear('journal_entry__date'), label=F('account__category__name')).values('year',
                                                                                                                 'label').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')
        if group_by == 'type':
            qs = qs.annotate(year=ExtractYear('journal_entry__date'),
                             label=F('journal_entry__content_type__model')).values('year', 'label').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')
        return qs

    @action(detail=False)
    def export(self, request):
        queryset = self.get_queryset().order_by('-journal_entry__date')
        if not request.GET.get('group'):
            params = [
                ('Transactions', queryset, TransactionResource)
            ]
            return qs_to_xls(params)
        else:
            params = [
                ('Transactions', queryset, TransactionGroupResource)
            ]
            return qs_to_xls(params)


class AccountClosingViewSet(CollectionViewSet, ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = AccountClosing.objects.all()
    serializer_class = AccountClosingSerializer

    collections = [
        ('fiscal_years', FiscalYear)
    ]

    def get_defaults(self, request=None):
        company = request.company
        current_fiscal_year_id = company.current_fiscal_year_id
        return {
            'fields': {
                'current_fiscal_year_id': current_fiscal_year_id
            }
        }

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.company)
    
    def create(self, request, *args, **kwargs):
        company = request.company
        fiscal_year_id = request.data.get('fiscal_year')
        account_closing = AccountClosing.objects.get_or_create(company=company, fiscal_period_id=fiscal_year_id)[0]
        if account_closing.status == 'Closed':
            return Response({'detail': 'Your accounts for this year have already been closed.'}, status=400)
        account_closing.close()
        return Response('Successfully closed accounts for selected fiscal year.', status=200)
        
