from datetime import datetime

from django.db.models import Sum, Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models import JournalEntry, Transaction
from apps.ledger.serializers import JournalEntryMultiAccountSerializer, TransactionEntrySerializer
from awecount.utils import delete_rows
from awecount.utils.CustomViewSet import GenericSerializer
from awecount.utils.serializers import ShortNameChoiceSerializer


class InputChoiceMixin(object):
    @action(detail=False)
    def choices(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if hasattr(self, 'choice_serializer_class'):
            serializer_class = self.choice_serializer_class
        else:
            serializer_class = GenericSerializer
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)


class ShortNameChoiceMixin(object):
    def get_serializer_context(self):
        extra_fields = self.extra_fields if hasattr(self, 'extra_fields') else None
        return {
            'extra_fields': extra_fields
        }

    def get_serializer_class(self):
        if self.action in ('choices',):
            return ShortNameChoiceSerializer
        return super().get_serializer_class()


class DeleteRows(object):
    def update(self, request, *args, **kwargs):
        params = request.data
        if hasattr(self, 'row'):
            row_class = self.row
        else:
            row_class = self.queryset.model.rows.field.model
        delete_rows(params.get('deleted_rows', None), row_class)
        return super(DeleteRows, self).update(request, *args, **kwargs)


class TransactionsViewMixin(object):
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        param = request.GET
        obj = self.get_object()
        serializer_class = self.get_serializer_class()
        data = serializer_class(obj).data
        account_ids = self.get_account_ids(obj)
        start_date = param.get('start_date', None)
        end_date = param.get('end_date', None)
        transactions = Transaction.objects.filter(account_id__in=account_ids).order_by('-journal_entry__date', '-pk') \
            .select_related('journal_entry__content_type').prefetch_related(
            Prefetch('journal_entry__transactions', Transaction.objects.select_related('account')))

        aggregate = {}
        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date == end_date:
                transactions = transactions.filter(journal_entry__date=start_date)
            else:
                transactions = transactions.filter(journal_entry__date__range=[start_date, end_date])
            aggregate['total'] = transactions.aggregate(Sum('dr_amount'), Sum('cr_amount'))
            aggregate['opening'] = Transaction.objects.select_related('journal_entry__content_type').filter(
                account_id__in=account_ids, journal_entry__date__lte=start_date).aggregate(Sum('dr_amount'), Sum('cr_amount'))

        page_size = param.get('page_size', None)
        if page_size and page_size.is_integer():
            self.paginator.page_size = int(page_size)
        page = self.paginate_queryset(transactions)
        serializer = TransactionEntrySerializer(page, many=True)
        data['transactions'] = self.paginator.get_response_data(serializer.data)
        data['aggregate'] = aggregate
        return Response(data)
