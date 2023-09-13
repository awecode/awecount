from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
import datetime

from django.http import HttpResponse
from django.db.models import (
    Sum,
    F,
    Case,
    When,
    Value,
    Q,
)
from django.utils import timezone

from apps.ledger.models.base import Party
from apps.ledger.serializers import PartySerializer
from apps.voucher.models import SalesVoucher


def merge_dict_lists(lists, k):
    merged_data = {}
    for lst in lists:
        for dct in lst:
            current_id = dct[k]
            if current_id in merged_data:
                merged_data[current_id].update(dct)
            else:
                merged_data[current_id] = dct

    merged_list = list(merged_data.values())
    return merged_list


class ReportViewSet(GenericViewSet):
    serializer_class = PartySerializer

    def get_queryset(self):
        company = self.request.company
        queryset = (
            Party.objects.select_related("customer_account", "company")
            .filter(company=company)
            .filter(customer_account_id__isnull=False)
        )
        return queryset
    
    def ageing_report_data(selg, request):
        base_date_str =  request.query_params["date"]
        base_date = datetime.datetime.strptime(base_date_str, "%Y-%m-%d")
        date_range_30 = [base_date - timezone.timedelta(days=30), base_date]
        date_range_60 = [
            base_date - timezone.timedelta(days=60),
            base_date - timezone.timedelta(days=30),
        ]
        date_range_90 = [
            base_date - timezone.timedelta(days=90),
            base_date - timezone.timedelta(days=60),
        ]
        date_range_120 = [
            base_date - timezone.timedelta(days=120),
            base_date - timezone.timedelta(days=90),
        ]
        date_120plus = base_date - timezone.timedelta(days=120)

        status_case_expr = Case(
            When(
                payment_receipts__amount__lt=F("total_amount"),
                then=Value("Partially Paid"),
            ),
            default=Value("Unpaid"),
        )

        amount_case_expr = Case(
            When(
                payment_status="Partially Paid",
                then=F("total_amount") - F("payment_receipts__amount"),
            ),
            default=F("total_amount"),
        )

        total_30 = (
            (
                SalesVoucher.objects.filter(company=request.company).exclude(status__in=["Cancelled", "Draft"])
                .filter(mode="Credit", date__range=date_range_30)
                .filter(Q(payment_date__isnull=True) | ~Q(payment_date__lte=base_date))
                .annotate(party_name=F("party__name"))
                .annotate(payment_status=status_case_expr)
            )
            .annotate(amount_due=amount_case_expr)
            .values("party_name", "party_id")
            .annotate(total_30=Sum("total_amount"))
        )

        total_60 = (
            (
                SalesVoucher.objects.filter(company=request.company).exclude(status__in=["Cancelled", "Draft"])
                .filter(mode="Credit", date__range=date_range_60)
                .filter(
                    Q(payment_date__isnull=True)
                    | ~Q(payment_date__lte=base_date - timezone.timedelta(days=30))
                )
                .annotate(party_name=F("party__name"))
                .annotate(payment_status=status_case_expr)
            )
            .annotate(amount_due=amount_case_expr)
            .values("party_name", "party_id")
            .annotate(total_60=Sum("total_amount"))
        )

        total_90 = (
            (
                SalesVoucher.objects.filter(company=request.company).exclude(status__in=["Cancelled", "Draft"])
                .filter(mode="Credit", date__range=date_range_90)
                .filter(
                    Q(payment_date__isnull=True)
                    | ~Q(payment_date__lte=base_date - timezone.timedelta(days=60))
                )
                .annotate(party_name=F("party__name"))
                .annotate(payment_status=status_case_expr)
            )
            .annotate(amount_due=amount_case_expr)
            .values("party_name", "party_id")
            .annotate(total_90=Sum("total_amount"))
        )

        total_120 = (
            (
                SalesVoucher.objects.filter(company=request.company).exclude(status__in=["Cancelled", "Draft"])
                .filter(mode="Credit", date__range=date_range_120)
                .filter(
                    Q(payment_date__isnull=True)
                    | ~Q(payment_date__lte=base_date - timezone.timedelta(days=90))
                )
                .annotate(party_name=F("party__name"))
                .annotate(payment_status=status_case_expr)
            )
            .annotate(amount_due=amount_case_expr)
            .values("party_name", "party_id")
            .annotate(total_120=Sum("total_amount"))
        )

        total_120plus = (
            (
                SalesVoucher.objects.filter(company=request.company).exclude(status__in=["Cancelled", "Draft"])
                .filter(mode="Credit", date__lte=date_120plus)
                .filter(
                    Q(payment_date__isnull=True)
                    | ~Q(payment_date__lte=base_date - timezone.timedelta(days=120))
                )
                .annotate(party_name=F("party__name"))
                .annotate(payment_status=status_case_expr)
            )
            .annotate(amount_due=amount_case_expr)
            .values("party_name", "party_id")
            .annotate(total_120plus=Sum("total_amount"))
        )

        lists = [total_30, total_60, total_90, total_120, total_120plus]
        merge_dicts = merge_dict_lists(lists, "party_name")
        ret_dicts = []
        keys = ["total_30", "total_60", "total_90", "total_120", "total_120plus", "grand_total"]
        for dict in merge_dicts:
            dct = {}
            for key in keys:
                dct[key] = 0
            for k, v in dict.items():
                dct[k] = v
                if k.startswith("total"):
                    dct["grand_total"] += v
            ret_dicts.append(dct)
        return ret_dicts

    @action(detail=False, methods=["GET"], url_path="ageing-report")
    def ageing_report(self, request):
        ret_dicts = self.ageing_report_data(request)
        page = self.paginate_queryset(ret_dicts)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(ret_dicts)
    
    @action(detail=False, methods=["GET"], url_path="export-ageing-report")
    def export_ageing_report(self, request):
        ret_dicts = self.ageing_report_data(request)
        for dct in ret_dicts:
            dct.pop("party_id")

        from xlsxwriter import Workbook
        headers = {
            "party_name": "Party",
            "total_30": "30 days",
            "total_60": "60 days",
            "total_90": "90 days",
            "total_120": "120 days",
            "total_120plus": "120 days +",
            "grand_total": "Total"
        }
        aggregate = {
            "party_name": "Total",
            "total_30": 0,
            "total_60": 0,
            "total_90": 0,
            "total_120": 0,
            "total_120plus": 0,
            "grand_total": 0
        }
        for dct in ret_dicts:
            for k, v in dct.items():
                if not isinstance(v, str):
                    aggregate[k] += v
        wb = Workbook("ageing_report.xlsx")
        ws = wb.add_worksheet("report")
        first_row = 0
        headers_list = [v for k, v in headers.items()]
        for header in headers_list:
            col = headers_list.index(header)
            ws.write(first_row, col, header)
        row = 1
        for dict in ret_dicts:
            for key, value in dict.items():
                col=headers_list.index(headers[key])
                ws.write(row, col, value)
            row += 1
        for k, v in aggregate.items():
            col = headers_list.index(headers[k])
            ws.write(row, col, v)
        ws.set_row(first_row, None, wb.add_format({'bold': True}))
        ws.set_row(row, None, wb.add_format({'bold': True}))
        wb.close()
        with open("ageing_report.xlsx", "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = 'Ageing_{}.xlsx'.format(datetime.datetime.today().date())
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response

