from datetime import datetime

from django.db.models import Q, Sum, Case, When, F, Prefetch
from django_filters import rest_framework as filters
from mptt.utils import get_cached_trees
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ledger.filters import AccountFilterSet, CategoryFilterSet
from apps.tax.models import TaxScheme
from apps.voucher.models import SalesVoucher, PurchaseVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, TransactionsViewMixin
from .models import Account, JournalEntry, Category, AccountOpeningBalance, Transaction
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer, JournalEntrySerializer, \
    PartyMinSerializer, PartyAccountSerializer, CategoryTreeSerializer, AccountOpeningBalanceSerializer, \
    AccountOpeningBalanceListSerializer, AccountFormSerializer, PartyListSerializer


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
                dr=Sum('customer_account__transactions__dr_amount'), cr=Sum('customer_account__transactions__cr_amount'))
        if self.action == 'suppliers':
            qs = qs.filter(customer_account__transactions__isnull=False).annotate(
                dr=Sum('supplier_account__transactions__dr_amount'), cr=Sum('supplier_account__transactions__cr_amount'))
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
    filter_class = CategoryFilterSet

    collections = (
        ('categories', Category, CategorySerializer),
    )


class AccountViewSet(InputChoiceMixin, TransactionsViewMixin, CRULViewSet):
    serializer_class = AccountSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)
    filter_class = AccountFilterSet

    def get_account_ids(self, obj):
        return [obj.id]

    def get_queryset(self):
        # TODO View transaction with or without cr or dr amount
        # queryset = Account.objects.filter(Q(current_dr__gt=0)|Q(current_cr__gt=0), company=self.request.company)
        queryset = Account.objects.filter(company=self.request.company).select_related('category', 'parent')
        return queryset

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
            qq = Account.objects.filter(company=request.company).annotate(
                od=Sum('transactions__dr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                oc=Sum('transactions__cr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                cd=Sum('transactions__dr_amount', filter=Q(transactions__journal_entry__date__lte=end_date)),
                cc=Sum('transactions__cr_amount', filter=Q(transactions__journal_entry__date__lte=end_date)),
            ) \
                .values('id', 'name', 'category_id', 'od', 'oc', 'cd', 'cc').exclude(od=None, oc=None, cd=None, cc=None)
            return Response(list(qq))
        return Response({})


class TaxSummaryView(APIView):
    action = 'list'

    def get_queryset(self):
        return TaxScheme.objects.none()

    def get_sales_queryset(self, **kwargs):
        return SalesVoucher.objects.filter(company_id=self.request.company_id, status__in=['Issued', 'Paid', 'Partially Paid'])

    def get_non_import_purchase_queryset(self, **kwargs):
        return PurchaseVoucher.objects.filter(is_import=False).filter(Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0)).filter(
            company_id=self.request.company_id, status__in=['Issued', 'Paid', 'Partially Paid']).distinct()

    def get_import_purchase_queryset(self, **kwargs):
        return PurchaseVoucher.objects.filter(is_import=True).filter(Q(rows__item__can_be_sold=True) | Q(meta_tax__gt=0)).filter(
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

        import_purchase_data = self.get_import_purchase_queryset().filter(date__gte=start_date, date__lte=end_date).aggregate(
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
