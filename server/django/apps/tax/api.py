from rest_framework.fields import (  # NOQA # isort:skip
    IntegerField, )

from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, JournalEntriesMixin, ShortNameChoiceMixin


class TaxSchemeViewSet(InputChoiceMixin, ShortNameChoiceMixin, JournalEntriesMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = TaxSchemeSerializer
    account_keys = ['receivable', 'payable']
    extra_fields = {
        'rate': IntegerField
    }
