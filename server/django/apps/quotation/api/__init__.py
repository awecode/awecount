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
    SalesAgent,
)

from django_q.tasks import async_task
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed

from apps.users.serializers import CompanySerializer

from django.db.models import Prefetch, Q


from apps.voucher.serializers.sales import (
    SalesDiscountMinSerializer,
    SalesVoucherCreateSerializer,
)


from awecount.libs import get_next_quotation_no
from awecount.libs.CustomViewSet import (
    CRULViewSet,
    GenericSerializer,
)
from awecount.libs.helpers import (
    get_verification_hash,
    check_verification_hash,
)
from awecount.libs.mixins import (
    DeleteRows,
    InputChoiceMixin,
)
from apps.quotation.filters import QuotationFilterSet
from apps.quotation.models import Quotation, QuotationRow
from apps.quotation.serializers import (
    EmailQuotationRequestSerializer,
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
        "reference",
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

    def get_quotation_details(self, pk):
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
            .select_related("discount_obj", "company__sales_setting", "party")
        )
        data = QuotationDetailSerializer(
            get_object_or_404(pk=pk, queryset=qs), context={"request": self.request}
        ).data
        return data

    @action(detail=True)
    def details(self, request, pk, *args, **kwargs):
        details = self.get_quotation_details(pk)
        hash = get_verification_hash("quotation-{}".format(pk))
        return Response({**details, "hash": hash})

    @action(detail=True, permission_classes=[], url_path="details-by-hash")
    def details_by_hash(self, request, pk, *args, **kwargs):
        hash = request.GET.get("hash")
        if not hash:
            raise AuthenticationFailed("No hash provided")
        if check_verification_hash(hash, "quotation-{}".format(pk)) is False:
            raise AuthenticationFailed("Invalid hash")
        obj = Quotation.objects.get(pk=pk)
        self.request.company = obj.company
        self.request.company_id = obj.company_id
        details = self.get_quotation_details(pk)
        return Response({**details, "company": CompanySerializer(obj.company).data})

    @action(detail=True, url_path="email-quotation", methods=["POST"])
    def email_quotation(self, request, pk, *args, **kwargs):
        serializer = EmailQuotationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_object()
        async_task(
            "apps.quotation.models.Quotation.email_quotation",
            obj,
            **serializer.validated_data,
        )
        if obj.status == "Generated":
            obj.status = "Sent"
            obj.save()
        return Response({})

    @action(detail=True, url_path="create-a-copy", methods=["POST"])
    def create_a_copy(self, request, pk, *args, **kwargs):
        """
        Create a copy of the Quotation
        """
        obj = self.get_object()
        data = QuotationCreateSerializer(obj).data
        data["number"] = None
        data["status"] = "Draft"
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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

    @action(detail=True, methods=["post"], url_path="convert")
    def convert_to_sales_voucher(self, request, *args, **kwargs):
        """
        Convert Quotation to Sales Voucher
        """
        obj = self.get_object()
        if obj.status == "Draft":
            return Response({"details": "Quotation is in draft state"}, status=400)
        if obj.status == "Converted":
            return Response({"details": "Quotation already converted"}, status=400)

        quotation_data = QuotationDetailSerializer(obj).data

        validated_data = SalesVoucherCreateSerializer(
            data={
                **quotation_data,
                "status": "Draft",
                "quotation": obj.id,
            },
            context={"request": request},
        )
        if validated_data.is_valid():
            validated_data.save()
            obj.status = "Converted"
            obj.save()
            return Response(validated_data.data, status=201)
        return Response(validated_data.errors, status=400)


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
