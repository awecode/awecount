from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as RESTValidationError
from rest_framework.response import Response

from apps.ledger.models import Transaction
from apps.ledger.serializers import TransactionEntrySerializer
from awecount.libs import delete_rows
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import ShortNameChoiceSerializer


class InputChoiceMixin(object):
    @action(detail=False)
    def choices(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_keyword = request.query_params.get("search")
        append_result_id = request.query_params.get("id")
        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)

        if append_result_id:
            queryset = queryset.exclude(id=append_result_id)

        paginator = self.paginator
        paginator.page_size = 30
        page = paginator.paginate_queryset(queryset, request)
        if hasattr(self, "choice_serializer_class"):
            serializer_class = self.choice_serializer_class
        else:
            serializer_class = GenericSerializer
        serializer = serializer_class(page, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        if append_result_id and int(request.query_params.get("page", 0)) < 2:
            result_qs = self.filter_queryset(self.get_queryset()).filter(
                id=append_result_id
            )
            result_serializer = serializer_class(result_qs, many=True)
            paginated_data.data["results"].extend(result_serializer.data)
        return paginated_data


class ShortNameChoiceMixin(object):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        extra_fields = self.extra_fields if hasattr(self, "extra_fields") else None
        context["extra_fields"] = extra_fields
        return context

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
    def transactions(self, request, pk=None, *args, **kwargs):
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

        # transactions = Transaction.objects.select_related('account').filter(account_id__in=account_ids).values(
        # 'journal_entry__source_voucher_id', 'journal_entry__content_type__model').order_by('journal_entry__source_voucher_id').annotate(
        #     count=Count('journal_entry__source_voucher_id'))

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

        transactions = Transaction.objects.raw(raw_query)
        opening_transaction = transactions

        aggregate = {}
        if start_date or end_date:
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


class CancelPurchaseVoucherMixin:
    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk, *args, **kwargs):
        purchase_voucher = self.get_object()
        message = request.data.get("message")
        if not message:
            raise RESTValidationError(
                {"message": "message field is required for cancelling invoice!"}
            )

        if purchase_voucher.debit_notes.exclude(status="Cancelled").exists():
            raise RESTValidationError(
                {
                    "message": "This purchase voucher has debit notes. Please cancel them first."
                }
            )

        # FIFO inconsistency check
        if (
            request.company.inventory_setting.enable_fifo
            and not request.query_params.get("fifo_inconsistency")
        ):
            raise UnprocessableException(
                detail="This may cause inconsistencies in fifo!",
                code="fifo_inconsistency",
            )

        # Negative stock check
        if (
            request.company.inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
            if purchase_voucher.rows.filter(
                item__account__current_balance__lt=0
            ).count():
                raise UnprocessableException(
                    detail="Negative Stock Warning!", code="negative_stock"
                )

        purchase_voucher.cancel()
        return Response({})


class CancelCreditOrDebitNoteMixin:
    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk, *args, **kwargs):
        if (
            request.company.inventory_setting.enable_fifo
            and not request.query_params.get("fifo_inconsistency")
        ):
            raise UnprocessableException(
                detail="This may cause inconsistencies in fifo!",
                code="fifo_inconsistency",
            )

        obj = self.get_object()
        try:
            obj.cancel()
            return Response({})
        except Exception as e:
            raise APIException(str(e))
