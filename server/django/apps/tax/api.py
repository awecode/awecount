from rest_framework.fields import (  # NOQA # isort:skip
    IntegerField, )

from apps.ledger.models import Account
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.filters import TaxPaymentFilterSet
from apps.tax.models import TaxScheme, STATUSES
from apps.tax.serializers import TaxSchemeSerializer, TaxPaymentSerializer, TaxSchemeMinSerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, TransactionsViewMixin, ShortNameChoiceMixin

from rest_framework import filters as rf_filters
from django_filters import rest_framework as filters


class TaxSchemeViewSet(InputChoiceMixin, ShortNameChoiceMixin, TransactionsViewMixin, CRULViewSet):
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

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'cr_account__name', 'date', 'tax_scheme__name', 'remarks', 'amount',]
    filterset_class = TaxPaymentFilterSet

    def get_queryset(self, **kwargs):
        return super().get_queryset().order_by('-id')
