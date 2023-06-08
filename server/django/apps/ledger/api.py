from datetime import datetime

from django.db.models import Q, Sum, Case, When, F, Max
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from mptt.utils import get_cached_trees
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.ledger.filters import AccountFilterSet, CategoryFilterSet, TransactionFilterSet
from apps.tax.models import TaxScheme
from apps.voucher.models import SalesVoucher, PurchaseVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from awecount.libs.CustomViewSet import CRULViewSet, CollectionViewSet, CompanyViewSetMixin
from awecount.libs.mixins import InputChoiceMixin, TransactionsViewMixin
from .models import Account, JournalEntry, Category, AccountOpeningBalance
from .serializers import ContentTypeListSerializer, PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer, \
    JournalEntrySerializer, \
    PartyMinSerializer, PartyAccountSerializer, CategoryTreeSerializer, AccountOpeningBalanceSerializer, \
    AccountOpeningBalanceListSerializer, AccountFormSerializer, PartyListSerializer, AccountListSerializer, TransactionEntrySerializer


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
    from django.contrib.contenttypes.models import ContentType
    company_id_attr = 'journal_entry__company_id'
    serializer_class = TransactionEntrySerializer
    filter_backends = [DjangoFilterBackend, rf_filters.SearchFilter]
    # filterset_class = TransactionFilterSet
    # search_fields = ['journal_entry__source__get_voucher_no']
    journal_entry_content_type = JournalEntry.objects.values_list('content_type', flat=True).distinct()
    # transaction_account = Transaction.objects.values_list('account', flat=True).distinct()
    # collections = [
    #     ('accounts', Account.objects.filter(id__in=transaction_account)),
    #     ('types', ContentType.objects.filter(id__in=journal_entry_content_type), ContentTypeListSerializer),
    # ]
    collections = [
        ('accounts', Account),
        ('transaction_types', ContentType.objects.filter(id__in=journal_entry_content_type), ContentTypeListSerializer),
        ('categories', Category)
    ]

    def get_queryset(self, company_id=None):
        qs = super().get_queryset().select_related('account', 'journal_entry__content_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        accounts = list(filter(None, self.request.GET.getlist('account')))
        categories = list(filter(None, self.request.GET.getlist('category')))
        sources = list(filter(None, self.request.GET.getlist('source')))
        if start_date and end_date:
            qs = qs.filter(journal_entry__date__range=[start_date, end_date])
        if accounts:
            qs = qs.filter(account_id__in=accounts)
        if categories:
            qs = qs.filter(account__category_id__in=categories)
        if sources:
            qs = qs.filter(journal_entry__content_type_id__in=sources)
        return qs

    @action(['get'], detail=False, url_path='aggregate')
    def aggregate(self, request):
        from django.db.models.functions import ExtractYear
        from django.db.models import Sum, Func, CharField, Value

        model_map = {
            'purchasevoucherrow': 'Purchase Voucher Row',
            'incomerow': 'Income Row',
            'income': 'Income'
        }

        # params = request.body()
        group_by = request.GET.get('group_by')
        qs = super().get_queryset().select_related('account', 'journal_entry__content_type')
        if group_by == 'acc':
            qq = qs.annotate(year=ExtractYear('journal_entry__date')).values('year', 'account__name').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')
        if group_by == 'cat':
            qq = qs.annotate(year=ExtractYear('journal_entry__date')).values('year', 'account__category__name').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')
        if group_by == 'type':
            qq = qs.annotate(year=ExtractYear('journal_entry__date')).values('year', 'journal_entry__content_type__model').annotate(
                total_debit=Sum('dr_amount'),
                total_credit=Sum('cr_amount'),
            ).order_by('-year')

            # qq = qs.annotate(model_name=F('journal_entry__content_type__model')).values('model_name')

            # qq = qs\
            #     .annotate(year=ExtractYear('journal_entry__date'),\
            #               source_type = Case(
            #                 When(journal_entry__content_type__model__icontains='row', then='journal_entry__content_type__model'),
            #                 When(journal_entry__content_type__model__icontains='particular', then=Value('Particular')),
            #                 When(journal_entry__content_type__model__icontains='account', then=Value('Opening Balance')),
            #                 default= Value('Other')
                            
            #               ))\
            #     .values('year', 'account__name', 'source_type')\
            #     .annotate(
            #         total_debit=Sum('dr_amount'),
            #         total_credit=Sum('cr_amount'),
            #     )\
            #     .order_by('-year')
            
            page = self.paginate_queryset(qq)
            if page is not None:
                return self.get_paginated_response(page)
            return Response(qq)

        return Response('FO')