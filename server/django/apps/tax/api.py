from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.fields import (  # NOQA # isort:skip
    IntegerField, )
from rest_framework.response import Response

from apps.ledger.models import Account
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.filters import TaxPaymentFilterSet
from apps.tax.models import TaxScheme, STATUSES, TaxPayment
from apps.tax.serializers import TaxSchemeSerializer, TaxPaymentSerializer, TaxSchemeMinSerializer, \
    TaxAccountSerializer, TaxPaymentJournalEntrySerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, TransactionsViewMixin, ShortNameChoiceMixin

from rest_framework import filters as rf_filters
from django_filters import rest_framework as filters


class TaxSchemeViewSet(InputChoiceMixin, ShortNameChoiceMixin, TransactionsViewMixin, CRULViewSet):
    serializer_class = TaxSchemeSerializer
    extra_fields = {
        'rate': IntegerField
    }

    def get_account_ids(self, obj):
        if obj.recoverable:
            return [obj.receivable_id, obj.payable_id]
        return [obj.payable_id]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'transactions':
            qs = qs.select_related('receivable', 'payable')
        return qs

    def get_serializer_class(self):
        if self.action == 'transactions':
            return TaxAccountSerializer
        return TaxSchemeSerializer


class TaxPaymentViewSet(CRULViewSet):
    serializer_class = TaxPaymentSerializer
    collections = (
        ('cr_accounts', Account.get_creditable_accounts(), AccountMinSerializer),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
    )

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'cr_account__name', 'date', 'tax_scheme__name', 'remarks', 'amount', ]
    filterset_class = TaxPaymentFilterSet

    def get_queryset(self, **kwargs):
        return super().get_queryset().order_by('-id')

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        tax_payment = get_object_or_404(TaxPayment, pk=pk)
        journals = tax_payment.journal_entries()
        return Response(TaxPaymentJournalEntrySerializer(journals, many=True).data)
