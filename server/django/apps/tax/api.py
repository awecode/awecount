from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class TaxSchemeViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = TaxSchemeSerializer
    choice_fields = ('id', 'label')

