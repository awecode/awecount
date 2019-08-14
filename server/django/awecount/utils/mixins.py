from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models import JournalEntry
from apps.ledger.serializers import JournalEntryMultiAccountSerializer
from awecount.utils import delete_rows
from awecount.utils.serializers import ShortNameChoiceSerializer


class InputChoiceMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        if self.action in ('choices',):
            self._paginator = None
        return self._paginator

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        choice_fields = None
        if hasattr(self, 'choice_fields'):
            choice_fields = self.choice_fields
        if self.action in ('choices',):
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(detail=False)
    def choices(self, request):
        return self.list(request)


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
        delete_rows(params.get('deleted_rows', None), self.row)
        return super(DeleteRows, self).update(request, *args, **kwargs)


class JournalEntriesMixin(object):

    def get_account_ids(self, object):
        account_ids = []
        for attribute in self.account_keys:
            account = getattr(object, attribute)
            if account:
                account_ids.append(account.id)
        return account_ids

    @action(detail=True, methods=['get'])
    def accounts(self, request, pk=None):
        param = request.GET
        object = self.get_object()
        data = self.serializer_class(object).data
        account_ids = self.get_account_ids(object)
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
