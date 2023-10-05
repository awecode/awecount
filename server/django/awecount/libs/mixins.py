from datetime import datetime

from django.db.models import Sum, Prefetch, Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models import Transaction
from apps.ledger.serializers import TransactionEntrySerializer
from awecount.libs import delete_rows
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.serializers import ShortNameChoiceSerializer


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


# TODO Security Check
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

        account_id_list_str = ','.join([str(account_id) for account_id in account_ids])

        # transactions = Transaction.objects.select_related('account').filter(account_id__in=account_ids).values(
        # 'journal_entry__source_voucher_id', 'journal_entry__content_type__model').order_by('journal_entry__source_voucher_id').annotate(
        #     count=Count('journal_entry__source_voucher_id'))

        raw_query = f"""
        WITH AccountAggregation AS (
        SELECT
            je.source_voucher_id,
            ARRAY_AGG(DISTINCT t.account_id) AS account_ids,
            STRING_AGG(DISTINCT acc.name, 'ǯ') AS account_names
        FROM
            ledger_transaction AS t
        JOIN
            ledger_journalentry AS je ON t.journal_entry_id = je.id
        JOIN
            ledger_account AS acc ON t.account_id = acc.id
        WHERE
            t.account_id NOT IN ({account_id_list_str})
        GROUP BY
            je.source_voucher_id,
            je.date
    )

    SELECT
        1 as id,
        je.source_voucher_id as source_id,
        ct.model AS content_type_model,
        SUM(t.dr_amount) AS total_dr_amount,
        SUM(t.cr_amount) AS total_cr_amount,
        aa.account_ids,
        aa.account_names
    FROM
        ledger_transaction AS t
    JOIN
        ledger_journalentry AS je ON t.journal_entry_id = je.id
    JOIN
        django_content_type AS ct ON je.content_type_id = ct.id
    LEFT JOIN
        AccountAggregation AS aa ON je.source_voucher_id = aa.source_voucher_id
    WHERE
        t.account_id IN ({account_id_list_str})
    GROUP BY
        je.source_voucher_id,
        je.date,
        ct.model,
        aa.account_ids,
        aa.account_names
    ORDER BY
        je.date DESC
        """



        transactions = Transaction.objects.raw(raw_query)

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
        serializer = TransactionEntrySerializer(page, many=True)
        data['transactions'] = self.paginator.get_response_data(serializer.data)
        data['aggregate'] = aggregate
        return Response(data)
