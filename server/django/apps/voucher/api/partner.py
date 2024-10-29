from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.voucher.models import PurchaseVoucher
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.partner import (
    PartnerPurchaseDiscountSerializer,
    PartnerPurchaseVoucherCreateSerializer,
)


class PartnerPurchaseVoucherViewset(
    viewsets.GenericViewSet,
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
    
    # @action(detail=True, methods=["POST"])
    # def cancel(self, request, pk):
    #     purchase_voucher = self.get_object()
    #     message = request.data.get("message")
    #     if not message:
    #         raise RESTValidationError(
    #             {"message": "message field is required for cancelling invoice!"}
    #         )

    #     if purchase_voucher.debit_notes.exists():
    #         raise RESTValidationError(
    #             {
    #                 "message": "This purchase voucher has debit notes. Please cancel them first."
    #             }
    #         )

    #     # FIFO inconsistency check
    #     if (
    #         request.company.inventory_setting.enable_fifo
    #         and not request.query_params.get("fifo_inconsistency")
    #     ):
    #         raise UnprocessableException(
    #             detail="This may cause inconsistencies in fifo!",
    #             code="fifo_inconsistency",
    #         )

    #     # Negative stock check
    #     if (
    #         request.company.inventory_setting.enable_negative_stock_check
    #         and not request.query_params.get("negative_stock")
    #     ):
    #         if purchase_voucher.rows.filter(
    #             item__account__current_balance__lt=0
    #         ).count():
    #             raise UnprocessableException(
    #                 detail="Negative Stock Warning!", code="negative_stock"
    #             )

    #     purchase_voucher.cancel()
    #     return Response({})


class PartnerPurchaseDiscountViewset(viewsets.GenericViewSet):
    queryset = PurchaseDiscount.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        parties = self.queryset.filter(company_id=request.company_id).order_by("-pk")
        return Response(PartnerPurchaseDiscountSerializer(parties, many=True).data)
