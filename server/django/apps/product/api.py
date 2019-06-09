from apps.product.serializers import ItemSerializer, UnitSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class ItemViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer


class UnitViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = UnitSerializer
