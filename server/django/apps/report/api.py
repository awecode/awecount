from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

import datetime
from django.db.models import (
    Sum,
    F,
    ExpressionWrapper,
    DecimalField,
    Case,
    When,
    Value,
    Q,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.ledger.models.base import Account, Party
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

    @action(detail=False, methods=["GET"], url_path="ageing-report")
    def ageing_report(self, request):
        
        # base_date = (timezone.now() - timezone.timedelta(days=12)).date()
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
                SalesVoucher.objects.exclude(status__in=["Cancelled", "Draft"])
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
                SalesVoucher.objects.exclude(status__in=["Cancelled", "Draft"])
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
                SalesVoucher.objects.exclude(status__in=["Cancelled", "Draft"])
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
                SalesVoucher.objects.exclude(status__in=["Cancelled", "Draft"])
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
                SalesVoucher.objects.exclude(status__in=["Cancelled", "Draft"])
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
        return Response(ret_dicts)
