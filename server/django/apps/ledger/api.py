from datetime import datetime

from django.db.models import Q, Sum
from django_filters import rest_framework as filters
from mptt.utils import get_cached_trees
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ledger.filters import AccountFilterSet, CategoryFilterSet
from apps.voucher.models import SalesVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, TransactionsViewMixin
from .models import Account, JournalEntry, Category, AccountOpeningBalance
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer, JournalEntrySerializer, \
    PartyMinSerializer, PartyAccountSerializer, CategoryTreeSerializer, AccountOpeningBalanceSerializer


class PartyViewSet(InputChoiceMixin, TransactionsViewMixin, CRULViewSet):
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
        return PartySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'transactions':
            qs = qs.select_related('supplier_account', 'customer_account')
        return qs

    @action(detail=True)
    def sales_vouchers(self, request, pk=None):
        sales_vouchers = SalesVoucher.objects.filter(party_id=pk)
        data = SaleVoucherOptionsSerializer(sales_vouchers, many=True).data
        return Response(data)


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


class AccountOpeningBalanceViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = AccountOpeningBalanceSerializer

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('account__name', 'opening_balance',)

    def get_queryset(self):
        # TODO IF current_fiscal_year is updated in company
        queryset = AccountOpeningBalance.objects.filter(
            company__current_fiscal_year=self.request.company.current_fiscal_year)
        return queryset

    collections = (
        ('accounts', Account),
    )
