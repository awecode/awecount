from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.voucher.models import PurchaseVoucher
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.partner import (
    PartnerCreditNoteCreateSerializer,
    PartnerDebitNoteCreateSerializer,
    PartnerPurchaseDiscountSerializer,
    PartnerPurchaseVoucherCreateSerializer,
)
from awecount.libs.CustomViewSet import CompanyViewSetMixin
from awecount.libs.mixins import CancelPurchaseVoucherMixin


class PartnerPurchaseVoucherViewset(
    viewsets.GenericViewSet,
    CancelPurchaseVoucherMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = PartnerPurchaseVoucherCreateSerializer
    queryset = PartnerPurchaseVoucherCreateSerializer.Meta.model.objects.all()

    def create(self, request, *args, **kwargs):
        voucher_no = request.data.get("voucher_no", None)
        party_id = request.data.get("party", None)
        fiscal_year = request.company.current_fiscal_year
        if PurchaseVoucher.objects.filter(
            voucher_no=voucher_no, party_id=party_id, fiscal_year=fiscal_year
        ).exists():
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
                | Q(party__tax_registration_number__icontains=search_params)
                | Q(rows__item__name__icontains=search_params)
            )

        return qs.filter(company_id=self.request.company_id).order_by("-date", "-pk")


class PartnerPurchaseDiscountViewset(viewsets.GenericViewSet):
    queryset = PurchaseDiscount.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        parties = self.queryset.filter(company_id=request.company_id).order_by("-pk")
        return Response(PartnerPurchaseDiscountSerializer(parties, many=True).data)


class PartnerCreditNoteViewset(
    CompanyViewSetMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = PartnerCreditNoteCreateSerializer


class PartnerDebitNoteViewset(
    CompanyViewSetMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = PartnerDebitNoteCreateSerializer
    queryset = PartnerDebitNoteCreateSerializer.Meta.model.objects.all(
)