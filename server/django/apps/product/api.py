from rest_framework import filters

from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.product.models import Item
from apps.product.serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer, \
    ItemDetailSerializer

from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin


class ItemViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'description', 'search_data']
    detail_serializer_class = ItemDetailSerializer

    @action(detail=True)
    def details(self, request, pk=None):
        item = get_object_or_404(Item, pk=pk)
        serializer = self.detail_serializer_class(item, context={'request': request}).data
        return Response(serializer)


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = InventoryCategorySerializer


class BrandViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = BrandSerializer
