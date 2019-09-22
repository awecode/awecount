from datetime import datetime

from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters

from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.ledger.models import Account
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.models import TaxScheme
from apps.tax.serializers import  TaxSchemeMinSerializer
from .filters import ItemFilterSet
from .models import Item, JournalEntry, Category, Brand, Unit
from .serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer, \
    ItemDetailSerializer, InventoryAccountSerializer, JournalEntrySerializer, BookSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin
from .models import Category as InventoryCategory


class ItemViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price',]
    filterset_class = ItemFilterSet

    detail_serializer_class = ItemDetailSerializer

    collections = (
        ('brands', Brand, BrandSerializer),
        ('inventory_categories', InventoryCategory, InventoryCategorySerializer),
        ('units', Unit, UnitSerializer),
        ('accounts', Account, AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer)
    )

    @action(detail=True)
    def details(self, request, pk=None):
        item = get_object_or_404(queryset=super().get_queryset(), pk=pk)
        serializer = self.detail_serializer_class(item, context={'request': request}).data
        return Response(serializer)


class BookViewSet(InputChoiceMixin, CRULViewSet):
    collections = (
        ('brands', Brand, BrandSerializer),
    )

    filter_backends = (filters.DjangoFilterBackend, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price', ]
    filterset_class = ItemFilterSet

    def get_queryset(self, **kwargs):
        queryset = Item.objects.filter(category__name="Book", company=self.request.company)
        return queryset

    serializer_class = BookSerializer

    @action(detail=False)
    def category(self, request):
        import ipdb
        ipdb.set_trace()
        cat = Category.objects.get(company=self.request.company, name="Book")
        return Response(InventoryCategorySerializer(cat).data)


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CRULViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = InventoryCategorySerializer
    collections = (
        ('units', Unit, UnitSerializer),
        ('accounts', Account, AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer)
    )


class BrandViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = BrandSerializer


class InventoryAccountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = InventoryAccountSerializer

    filter_backends = (filters.DjangoFilterBackend, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)

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
