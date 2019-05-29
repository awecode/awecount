from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, JournalEntriesMixin


class TaxSchemeViewSet(InputChoiceMixin, JournalEntriesMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = TaxSchemeSerializer
    account_keys = ['receivable', 'payable']
