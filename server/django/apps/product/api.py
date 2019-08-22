from datetime import datetime

from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.product.models import Item, JournalEntry, Category
from apps.product.serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer, \
    ItemDetailSerializer, InventoryAccountSerializer, JournalEntrySerializer, BookSerializer

from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin


class ItemFilterSet(filters.FilterSet):
    class Meta:
        model = Item
        fields = ('can_be_sold', 'can_be_purchased')


class ItemViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data']
    filterset_class = ItemFilterSet
    detail_serializer_class = ItemDetailSerializer

    @action(detail=True)
    def details(self, request, pk=None):
        item = get_object_or_404(Item, pk=pk)
        serializer = self.detail_serializer_class(item, context={'request': request}).data
        return Response(serializer)


class BookViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):

    def get_queryset(self):
        queryset = Item.objects.filter(category__name="Book", company=self.request.company)
        return queryset

    serializer_class = BookSerializer

    @action(detail=False)
    def category(self, request):
        cat = Category.objects.get(company=self.request.company, name="Book")
        return Response(InventoryCategorySerializer(cat).data)


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = InventoryCategorySerializer


class BrandViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = BrandSerializer


class InventoryAccountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    filter_backends = (SearchFilter,)
    search_fields = ('code', 'name',)
    serializer_class = InventoryAccountSerializer

    @action(detail=True, methods=['get'], url_path='journal-entries')
    def journal_entries(self, request, pk=None):

        param = request.GET
        start_date = param.get('start_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = param.get('end_date')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        obj = self.get_object()
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()
        if start_date == end_date:
            entries = entries.filter(date=start_date)
        else:
            entries = entries.filter(date__range=[start_date, end_date])
        serializer = JournalEntrySerializer(entries, context={'account': obj}, many=True)
        return Response(serializer.data)
