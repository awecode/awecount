from django.db.models import Count
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
        if hasattr(self, "choice_serializer_class"):
            serializer_class = self.choice_serializer_class
        else:
            serializer_class = GenericSerializer
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)


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
    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        param = request.GET
        obj = self.get_object()
        serializer_class = self.get_serializer_class()
        data = serializer_class(obj).data
        account_ids = self.get_account_ids(obj)
        start_date = param.get("start_date", None)
        end_date = param.get("end_date", None)
        # page = int(param.get('page', 1))
        # page_size = int(param.get('page_size', 20))

        account_id_list_str = ",".join([str(account_id) for account_id in account_ids])

        transactions = Transaction.objects.select_related('account').filter(account_id__in=account_ids).values(
        'journal_entry__source_voucher_id', 'journal_entry__content_type__model').order_by('journal_entry__source_voucher_id').annotate(
            count=Count('journal_entry__source_voucher_id'))

        # FIXME: upgrade postgres and add this query back inside rawquery
        # -- CREATE OR REPLACE FUNCTION merge_jsonb_agg(jsonb, jsonb)
        #     RETURNS jsonb AS $$
        #         BEGIN
        #             RETURN (SELECT jsonb_agg(DISTINCT value) FROM jsonb_array_elements(COALESCE($1, '[]') || COALESCE($2, '[]')) AS value);
        #         END;
        # $$ LANGUAGE plpgsql;
        # -- CREATE OR REPLACE AGGREGATE jsonb_concat(jsonb) ( SFUNC = merge_jsonb_agg, STYPE = jsonb, INITCOND = '[]' );

        raw_query = f"""
        WITH SourceAggregation AS (
            WITH AccountAggregation AS (
                SELECT
                    je.id AS journal_entry_id,
                    je.source_voucher_id,
                    je.source_voucher_no,
                    je.date,
                    ct.model AS content_type_model,
                    ct.app_label AS content_type_app_label,
                    JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT('id', acc.id, 'name', acc.name)) AS accounts
                FROM
                    ledger_transaction AS t
                JOIN
                    ledger_journalentry AS je ON t.journal_entry_id = je.id
                JOIN
                    ledger_account AS acc ON t.account_id = acc.id
                JOIN
                    django_content_type AS ct ON je.content_type_id = ct.id
                WHERE
                    t.account_id NOT IN ({account_id_list_str})
                    {"AND je.date >= '" + start_date + "'" if start_date else ''}
                    {"AND je.date <= '" + end_date + "'" if end_date else ''}
                GROUP BY
                    je.id, je.source_voucher_id, je.date, ct.model, ct.app_label
            )
            SELECT
                SUM(t.id) as id,
                aa.source_voucher_id as source_id,
                aa.source_voucher_no as voucher_no,
                aa.content_type_model as content_type_model,
                aa.content_type_app_label as content_type_app_label,
                SUM(t.dr_amount) AS total_dr_amount,
                SUM(t.cr_amount) AS total_cr_amount,
                aa.date,
                aa.accounts AS accounts
            FROM
                ledger_transaction AS t
            JOIN
                AccountAggregation AS aa ON t.journal_entry_id = aa.journal_entry_id
            WHERE
                t.account_id IN ({account_id_list_str})
            GROUP BY
                aa.source_voucher_id,
                aa.source_voucher_no,
                aa.date,
                aa.content_type_model,
                aa.content_type_app_label,
                aa.accounts
        )
        SELECT
            SUM(sa.id) AS id,
            sa.source_id,
            sa.voucher_no,
            SUM(sa.total_dr_amount) AS total_dr_amount,
            SUM(sa.total_cr_amount) AS total_cr_amount,
            sa.content_type_model,
            sa.content_type_app_label,
            JSONB_CONCAT(sa.accounts)::json as accounts,
            sa.date
        FROM
            SourceAggregation AS sa
        GROUP BY
            sa.source_id,
            sa.voucher_no,
            sa.content_type_model,
            sa.content_type_app_label,
            sa.date
        ORDER BY
            sa.date DESC
        """

        # transactions = Transaction.objects.raw(raw_query)
        opening_transaction = transactions

        aggregate = {}
        if False and (start_date or end_date):
            if start_date:
                opening_transaction_query = f"""
                    WITH SourceAggregation AS (
                        WITH AccountAggregation AS (
                            SELECT
                                je.id AS journal_entry_id,
                                je.source_voucher_id,
                                je.date,
                                ct.model AS content_type_model,
                                ct.app_label AS content_type_app_label,
                                JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT('id', acc.id, 'name', acc.name)) AS accounts
                            FROM
                                ledger_transaction AS t
                            JOIN
                                ledger_journalentry AS je ON t.journal_entry_id = je.id
                            JOIN
                                ledger_account AS acc ON t.account_id = acc.id
                            JOIN
                                django_content_type AS ct ON je.content_type_id = ct.id
                            WHERE
                                t.account_id NOT IN ({account_id_list_str})
                                {"AND je.date < '" + start_date + "'" if start_date else ''}
                            GROUP BY
                                je.id, je.source_voucher_id, je.date, ct.model, ct.app_label
                        )
                        SELECT
                            SUM(t.id) as id,
                            aa.source_voucher_id as source_id,
                            SUM(t.dr_amount) AS total_dr_amount,
                            SUM(t.cr_amount) AS total_cr_amount,
                            aa.date
                        FROM
                            ledger_transaction AS t
                        JOIN
                            AccountAggregation AS aa ON t.journal_entry_id = aa.journal_entry_id
                        WHERE
                            t.account_id IN ({account_id_list_str})
                        GROUP BY
                            aa.source_voucher_id,
                            aa.date,
                            aa.accounts
                    )
                    SELECT
                        SUM(sa.id) AS id,
                        sa.source_id,
                        SUM(sa.total_dr_amount) AS total_dr_amount,
                        SUM(sa.total_cr_amount) AS total_cr_amount
                    FROM
                        SourceAggregation AS sa
                    GROUP BY
                        sa.source_id,
                        sa.date
                    ORDER BY
                        sa.date DESC
                    """
                opening_transaction = Transaction.objects.raw(opening_transaction_query)

            aggregate["opening"] = {
                "dr": sum(
                    [
                        t.total_dr_amount
                        for t in opening_transaction
                        if t.total_dr_amount is not None
                    ]
                ),
                "cr": sum(
                    [
                        t.total_cr_amount
                        for t in opening_transaction
                        if t.total_cr_amount is not None
                    ]
                ),
            }

            aggregate["total"] = {
                "dr": sum(
                    [
                        t.total_dr_amount
                        for t in transactions
                        if t.total_dr_amount is not None
                    ]
                ),
                "cr": sum(
                    [
                        t.total_cr_amount
                        for t in transactions
                        if t.total_cr_amount is not None
                    ]
                ),
            }

        page = self.paginate_queryset(transactions)
        serializer = TransactionEntrySerializer(page, many=True)
        data["transactions"] = self.paginator.get_response_data(serializer.data)
        data["aggregate"] = aggregate

        limit = self.paginator.page_size
        offset = (self.paginator.page.number - 1) * limit
        # transactions_from_previous_pages = transactions[:offset]
        transactions_from_next_pages = transactions[offset + limit :]
        data["page_cumulative"] = {
            "current": {
                "dr": sum(
                    [t.total_dr_amount for t in page if t.total_dr_amount is not None]
                ),
                "cr": sum(
                    [t.total_cr_amount for t in page if t.total_cr_amount is not None]
                ),
            },
            # 'previous': {
            #     'dr': sum(
            #         [t.total_dr_amount for t in transactions_from_previous_pages if t.total_dr_amount is not None]),
            #     'cr': sum(
            #         [t.total_cr_amount for t in transactions_from_previous_pages if t.total_cr_amount is not None])
            # },
            "next": {
                "dr": sum(
                    [
                        t.total_dr_amount
                        for t in transactions_from_next_pages
                        if t.total_dr_amount is not None
                    ]
                ),
                "cr": sum(
                    [
                        t.total_cr_amount
                        for t in transactions_from_next_pages
                        if t.total_cr_amount is not None
                    ]
                ),
            },
        }

        return Response(data)
