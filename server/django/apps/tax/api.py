from rest_framework.fields import (  # NOQA # isort:skip
    IntegerField, )

from apps.ledger.models import Account
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.models import TaxScheme, STATUSES
from apps.tax.serializers import TaxSchemeSerializer, TaxPaymentSerializer, TaxSchemeMinSerializer
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
    collections = (
        ('cr_accounts', Account, AccountMinSerializer),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
    )
