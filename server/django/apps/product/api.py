from apps.product.serializers import ItemSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet


class ItemViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = ItemSerializer
