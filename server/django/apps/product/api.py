from datetime import datetime

from django.conf import settings
from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.ledger.models import Account, Category as AccountCategory
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.models import TaxScheme
from apps.tax.serializers import TaxSchemeMinSerializer
from awecount.utils.CustomViewSet import CRULViewSet, GenericSerializer
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin
from .filters import ItemFilterSet, BookFilterSet, InventoryAccountFilterSet
from .models import Category as InventoryCategory, InventoryAccount
from .models import Item, JournalEntry, Category, Brand, Unit, Transaction
from .serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer, \
    ItemDetailSerializer, InventoryAccountSerializer, JournalEntrySerializer, BookSerializer, \
    TransactionEntrySerializer, \
    ItemPOSSerializer, ItemListSerializer, ItemOpeningSerializer


class ItemViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price', ]
    filterset_class = ItemFilterSet

    collections = (
        ('brands', Brand, BrandSerializer),
        ('inventory_categories', InventoryCategory, InventoryCategorySerializer),
        ('units', Unit, UnitSerializer),
        ('accounts', Account, AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer)
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.order_by('-id')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        return self.serializer_class

    @action(detail=True)
    def details(self, request, pk=None):
        item = get_object_or_404(queryset=super().get_queryset(), pk=pk)
        serializer = ItemDetailSerializer(item, context={'request': request}).data
        return Response(serializer)

    # items listing for POS
    @action(detail=False)
    def pos(self, request):
        self.filter_backends = (rf_filters.SearchFilter,)
        self.queryset = self.get_queryset().filter(can_be_sold=True)
        self.serializer_class = ItemPOSSerializer
        self.search_fields = ['name', 'code', 'description', 'search_data', ]
        self.paginator.page_size = settings.POS_ITEMS_SIZE
        return super().list(request)

    @action(detail=False, url_path='sales-choices')
    def sales_choices(self, request):
        queryset = self.get_queryset().filter(can_be_sold=True)
        serializer = GenericSerializer(queryset, many=True)
        return Response(serializer.data)


class ItemOpeningBalanceViewSet(CRULViewSet):
    serializer_class = ItemOpeningSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['item__name', 'item__code', 'item__description', 'item__search_data', 'opening_balance', ]
    filterset_class = InventoryAccountFilterSet
    collections = (
        ('items', Item.objects.filter(track_inventory=True), ItemListSerializer),
    )

    def get_queryset(self, company_id=None):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.filter(opening_balance__gt=0)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data
        account = get_object_or_404(InventoryAccount, item__id=data.get('item_id'), opening_balance=0, company=request.company)
        account.opening_balance = data.get('opening_balance')
        account.save()
        return Response({})


class BookViewSet(InputChoiceMixin, CRULViewSet):
    collections = (
        ('brands', Brand, BrandSerializer),
    )

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price', ]
    filterset_class = BookFilterSet

    def get_queryset(self, **kwargs):
        queryset = Item.objects.filter(category__name="Book", company=self.request.company)
        return queryset

    serializer_class = BookSerializer

    @action(detail=False)
    def category(self, request):
        cat = Category.objects.filter(company=self.request.company, name="Book").first()
        return Response(InventoryCategorySerializer(cat).data)


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CRULViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, ShortNameChoiceMixin, CRULViewSet):
    serializer_class = InventoryCategorySerializer
    collections = (
        ('units', Unit, UnitSerializer),
        ('accounts', Account, AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer),
    )

    def get_collections(self, request=None):
        collections_data = super().get_collections(self.request)
        collections_data['fixed_assets_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Fixed Assets', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        collections_data['direct_expenses_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Direct Expenses', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        collections_data['indirect_expenses_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Indirect Expenses', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        return collections_data

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.order_by('-id')
        return qs


class BrandViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = BrandSerializer


class InventoryAccountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = InventoryAccountSerializer

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)

    def get_account_ids(self, obj):
        return [obj.id]

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
        serializer = JournalEntrySerializer(entries, context={'account': obj}, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        param = request.GET
        obj = self.get_object()
        serializer_class = self.get_serializer_class()
        data = serializer_class(obj).data
        account_ids = self.get_account_ids(obj)
        start_date = param.get('start_date', None)
        end_date = param.get('end_date', None)
        transactions = Transaction.objects.filter(account_id__in=account_ids).order_by('-pk', '-journal_entry__date') \
            .select_related('journal_entry__content_type')

        aggregate = {}
        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date == end_date:
                transactions = transactions.filter(journal_entry__date=start_date)
            else:
                transactions = transactions.filter(journal_entry__date__range=[start_date, end_date])
            aggregate = transactions.aggregate(Sum('dr_amount'), Sum('cr_amount'))

        # Only show 5 because fetching voucher_no is expensive because of GFK
        self.paginator.page_size = 5
        page = self.paginate_queryset(transactions)
        serializer = TransactionEntrySerializer(page, many=True)
        data['transactions'] = self.paginator.get_response_data(serializer.data)
        data['aggregate'] = aggregate
        return Response(data)
