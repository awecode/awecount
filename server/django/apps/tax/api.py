from rest_framework.fields import (  # NOQA # isort:skip
    IntegerField, )

from apps.tax.serializers import TaxSchemeSerializer, TaxPaymentSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, JournalEntriesMixin, ShortNameChoiceMixin


class TaxSchemeViewSet(InputChoiceMixin, ShortNameChoiceMixin, JournalEntriesMixin, CRULViewSet):
    serializer_class = TaxSchemeSerializer
    account_keys = ['receivable', 'payable']
    extra_fields = {
        'rate': IntegerField
    }


class TaxPaymentViewSet(CRULViewSet):
    serializer_class = TaxPaymentSerializer
