from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.voucher.models import PaymentMode, PurchaseVoucher
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.partner import (
    PartnerCreditNoteCreateSerializer,
    PartnerDebitNoteCreateSerializer,
    PartnerPaymentModeSerializer,
    PartnerPurchaseDiscountSerializer,
    PartnerPurchaseVoucherCreateSerializer,
    PartnerPurchaseVoucherListSerializer,
)
from awecount.libs.CustomViewSet import CompanyViewSetMixin
from awecount.libs.mixins import (
    CancelCreditOrDebitNoteMixin,
    CancelPurchaseVoucherMixin,
)


class PartnerPurchaseVoucherViewSet(
    viewsets.GenericViewSet,
    CancelPurchaseVoucherMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = PartnerPurchaseVoucherCreateSerializer
    queryset = PartnerPurchaseVoucherCreateSerializer.Meta.model.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action in ("choices",):
            return PartnerPurchaseVoucherListSerializer
        return PartnerPurchaseVoucherCreateSerializer

    def create(self, request, *args, **kwargs):
        voucher_no = request.data.get("voucher_no", None)
        party_id = request.data.get("party", None)
        fiscal_year = request.company.current_fiscal_year
        if (
            voucher_no
            and PurchaseVoucher.objects.filter(
                voucher_no=voucher_no, party_id=party_id, fiscal_year=fiscal_year
            ).exists()
        ):
            raise ValidationError(
                {
                    "voucher_no": [
                        "Purchase with the bill number for the chosen party already exists."
                    ]
                }
            )
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        search_params = self.request.GET.get("q")
        if search_params:
            qs = qs.filter(
                Q(voucher_no__icontains=search_params)
                | Q(party__name__icontains=search_params)
                | Q(remarks__icontains=search_params)
                | Q(party__tax_identification_number__icontains=search_params)
                | Q(rows__item__name__icontains=search_params)
            )

        return qs.filter(company_id=self.request.company.id).order_by("-date", "-pk")


class PartnerPurchaseDiscountViewSet(viewsets.GenericViewSet):
    queryset = PurchaseDiscount.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request, *args, **kwargs):
        parties = self.queryset.filter(company_id=request.company.id).order_by("-pk")
        return Response(PartnerPurchaseDiscountSerializer(parties, many=True).data)


class PartnerCreditNoteViewSet(
    CompanyViewSetMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    CancelCreditOrDebitNoteMixin,
):
    serializer_class = PartnerCreditNoteCreateSerializer


class PartnerDebitNoteViewSet(
    CompanyViewSetMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    CancelCreditOrDebitNoteMixin,
):
    serializer_class = PartnerDebitNoteCreateSerializer
    queryset = PartnerDebitNoteCreateSerializer.Meta.model.objects.all()


class PartnerPaymentModeViewSet(viewsets.GenericViewSet):
    queryset = PaymentMode.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request, *args, **kwargs):
        enabled_for_purchase = request.GET.get("enabled_for_purchase", None) == "true"
        if enabled_for_purchase:
            self.queryset = self.queryset.filter(enabled_for_purchase=True)
        payment_modes = (
            self.queryset.filter(company_id=request.company.id)
            .order_by("-pk")
            .only("id", "name")
        )
        return Response(PartnerPaymentModeSerializer(payment_modes, many=True).data)
