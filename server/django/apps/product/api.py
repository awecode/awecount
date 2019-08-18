from rest_framework import filters

from apps.product.serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin


class ItemViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'description', 'search_data']


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = InventoryCategorySerializer


class BrandViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = BrandSerializer
