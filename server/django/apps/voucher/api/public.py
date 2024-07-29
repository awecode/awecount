from django.core.exceptions import ValidationError
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.voucher.models import PurchaseVoucher
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.public import (
    PublicPurchaseDiscountSerializer,
    PublicPurchaseVoucherCreateSerializer,
)


class PublicPurchaseVoucherViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = PublicPurchaseVoucherCreateSerializer
    queryset = PublicPurchaseVoucherCreateSerializer.Meta.model.objects.all()

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
        return self.queryset.filter(company_id=self.request.company_id)


class PublicPurchaseDiscountViewset(viewsets.GenericViewSet):
    queryset = PurchaseDiscount.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        parties = self.queryset.filter(company_id=request.company_id).order_by("-pk")
        return Response(PublicPurchaseDiscountSerializer(parties, many=True).data)
