from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models import JournalEntry
from apps.ledger.serializers import JournalEntryMultiAccountSerializer
from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class TaxSchemeViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = TaxSchemeSerializer

    @action(detail=True, methods=['get'])
    def accounts(self, request, pk=None):
        param = request.GET
        tax_scheme = self.get_object()
        data = self.serializer_class(tax_scheme).data
        account_ids = [
            tax_scheme.receivable.id,
            tax_scheme.payable.id,
        ]
        start_date = param.get('start_date', None)
        end_date = param.get('end_date', None)
        entries = JournalEntry.objects.filter(transactions__account_id__in=account_ids).order_by('pk',
                                                                                                 'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()
        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date == end_date:
                entries = entries.filter(date=start_date)
            else:
                entries = entries.filter(date__range=[start_date, end_date])
        entries = JournalEntryMultiAccountSerializer(entries, context={'account_ids': account_ids}, many=True).data
        data['entries'] = entries
        return Response(data)
