from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet


class TaxSchemeViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = TaxSchemeSerializer
