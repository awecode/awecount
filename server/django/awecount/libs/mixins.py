from datetime import datetime

from django.db.models import Sum, Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models import Transaction
from apps.ledger.serializers import TransactionQsEntrySerializer
from awecount.libs import delete_rows
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.serializers import ShortNameChoiceSerializer


class InputChoiceMixin(object):
    @action(detail=False)
    def choices(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        search_keyword = request.query_params.get("search")
        append_result_id = request.query_params.get("id")
        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)

        if append_result_id:
            queryset = queryset.exclude(id=append_result_id)

        paginator = self.paginator
        page = paginator.paginate_queryset(queryset, request)
        if hasattr(self, "choice_serializer_class"):
            serializer_class = self.choice_serializer_class
        else:
            serializer_class = GenericSerializer
        serializer = serializer_class(page, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        if append_result_id and int(request.query_params.get("page", 0)) < 2:
            result_qs = self.filter_queryset(self.get_queryset()).filter(id=append_result_id)
            result_serializer = serializer_class(result_qs, many=True)
            paginated_data.data["results"].extend(result_serializer.data)
        return paginated_data


class ShortNameChoiceMixin(object):
    def get_serializer_context(self):
        extra_fields = self.extra_fields if hasattr(self, "extra_fields") else None
        return {"extra_fields": extra_fields}

    def get_serializer_class(self):
        if self.action in ("choices",):
            return ShortNameChoiceSerializer
        return super().get_serializer_class()


# TODO Security Check
class DeleteRows(object):
    def update(self, request, *args, **kwargs):
        params = request.data
        if hasattr(self, "row"):
            row_class = self.row
        else:
            row_class = self.queryset.model.rows.field.model
        delete_rows(params.get("deleted_rows", None), row_class)
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
        transactions = Transaction.objects.filter(account_id__in=account_ids).order_by(
            '-journal_entry__date', '-pk') \
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
                account_id__in=account_ids, journal_entry__date__lte=start_date).aggregate(Sum('dr_amount'),
                                                                                           Sum('cr_amount'))

        page = self.paginate_queryset(transactions)
        serializer = TransactionQsEntrySerializer(page, many=True)
        data['transactions'] = self.paginator.get_response_data(serializer.data)
        data['aggregate'] = aggregate
        return Response(data)