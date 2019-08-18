from apps.product.serializers import ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, ShortNameChoiceMixin


class ItemViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = InventoryCategorySerializer


class BrandViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = BrandSerializer
