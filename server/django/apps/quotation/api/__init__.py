from apps.ledger.models import Party
from apps.ledger.serializers import (
    PartyMinSerializer,
)
from apps.product.models import Item, Unit
from apps.product.serializers import (
    ItemSalesSerializer,
)
from apps.tax.models import TaxScheme
from apps.tax.serializers import TaxSchemeMinSerializer

from apps.voucher.models import (
    PaymentReceipt,
    SalesAgent,
)

from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Prefetch, Q


from apps.voucher.serializers.sales import (
    SalesDiscountMinSerializer,
)


from awecount.libs import get_next_quotation_no
from awecount.libs.CustomViewSet import (
    CRULViewSet,
    GenericSerializer,
)
from awecount.libs.helpers import (
    get_verification_hash,
)
from awecount.libs.mixins import (
    DeleteRows,
    InputChoiceMixin,
)
from apps.quotation.filters import QuotationFilterSet
from apps.quotation.models import Quotation, QuotationRow
from apps.quotation.serializers import (
    QuotationChoiceSerializer,
    QuotationCreateSerializer,
    QuotationCreateSettingSerializer,
    QuotationSettingCreateSerializer,
    QuotationDetailSerializer,
    QuotationListSerializer,
    QuotationSettingUpdateSerializer,
    QuotationSettingsSerializer,
)
from apps.voucher.models.discounts import SalesDiscount


class QuotationViewSet(InputChoiceMixin, DeleteRows, CRULViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationCreateSerializer
    model = Quotation
    row = QuotationRow
    collections = [
        ("parties", Party, PartyMinSerializer, True, ["name"]),
        ("units", Unit, GenericSerializer, True, ["name"]),
        ("discounts", SalesDiscount, SalesDiscountMinSerializer, False),
        ("tax_schemes", TaxScheme, TaxSchemeMinSerializer, True, ["name"]),
        (
            "items",
            Item.objects.filter(
                Q(can_be_sold=True) | Q(direct_expense=True)
            ).select_related("unit"),
            ItemSalesSerializer,
            True,
            ["name"],
        ),
    ]

    filter_backends = [
        filters.DjangoFilterBackend,
        rf_filters.OrderingFilter,
        rf_filters.SearchFilter,
    ]

    filterset_class = QuotationFilterSet

    search_fields = [
        "number",
        "party__name",
        "remarks",
        "total_amount",
        "party__tax_identification_number",
        "customer_name",
        "date",
        "address",
        "rows__item__name",
    ]

    def get_collections(self, request=None, *args, **kwargs):
        sales_agent_tuple = ("sales_agents", SalesAgent)
        if (
            request.company.enable_sales_agents
            and sales_agent_tuple not in self.collections
        ):
            # noinspection PyTypeChecker
            self.collections.append(sales_agent_tuple)
        return super().get_collections(request)

    def get_queryset(self, **kwargs):
        qs = super(QuotationViewSet, self).get_queryset()
        if self.action == "retrieve":
            qs = qs.prefetch_related("rows", "rows__item", "rows__unit")
        elif self.action == "list":
            qs = qs.select_related("party")
        return qs.order_by("-date", "-number")

    def get_serializer_class(self):
        if self.action == "choices":
            return QuotationChoiceSerializer
        if self.action == "list":
            return QuotationListSerializer
        return QuotationCreateSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_voucher_details(self, pk):
        qs = (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "rows",
                    QuotationRow.objects.all()
                    .select_related(
                        "item", "item__category", "unit", "discount_obj", "tax_scheme"
                    )
                    .order_by("pk"),
                )
            )
            .prefetch_related(
                Prefetch(
                    "payment_receipts",
                    PaymentReceipt.objects.exclude(status="Cancelled"),
                    to_attr="receipts",
                )
            )
            .select_related("discount_obj", "company__sales_setting", "party")
        )
        data = QuotationDetailSerializer(
            get_object_or_404(pk=pk, queryset=qs), context={"request": self.request}
        ).data
        return data

    @action(detail=True)
    def details(self, request, pk, *args, **kwargs):
        details = self.get_voucher_details(pk)
        return Response(details)

    def get_defaults(self, request=None, *args, **kwargs):
        return {
            "options": {
                "enable_sales_agents": request.company.enable_sales_agents,
            },
        }

    def get_create_defaults(self, request=None, *args, **kwargs):
        data = QuotationCreateSettingSerializer(request.company.quotation_settings).data
        data["options"]["number"] = get_next_quotation_no(Quotation, request.company.id)
        return data

    def get_update_defaults(self, request=None, *args, **kwargs):
        data = QuotationSettingUpdateSerializer(request.company.quotation_settings).data
        obj = self.get_object()
        if not obj.number:
            data["options"]["number"] = get_next_quotation_no(
                Quotation, request.company.id
            )
        return data


class QuotationSettingsViewSet(CRULViewSet):
    serializer_class = QuotationSettingCreateSerializer

    def get_defaults(self, request=None, *args, **kwargs):
        q_setting = self.request.company.quotation_settings

        data = {
            "fields": QuotationSettingsSerializer(
                q_setting, context={"request": request}
            ).data,
        }
        return data
