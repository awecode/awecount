from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.models.base import Party
from apps.ledger.serializers.partner import (
    PartnerJournalVoucherCreateResponseSerializer,
    PartnerJournalVoucherCreateSerializer,
    PartnerJournalVoucherStatusChangeSerializer,
    PartnerPartyListSerializer,
    PartnerSalesVoucherAccessSerializer,
)
from apps.voucher.api import SalesVoucherViewSet
from apps.voucher.models.journal_vouchers import JournalVoucher


class PartnerJournalVoucherViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = PartnerJournalVoucherCreateSerializer
    queryset = PartnerJournalVoucherCreateSerializer.Meta.model.objects.all()

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        serializer = PartnerJournalVoucherCreateResponseSerializer(data=res.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="change-status")
    def change_status(self, request):
        serializer = PartnerJournalVoucherStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            journal_voucher = JournalVoucher.objects.get(
                voucher_no=serializer.validated_data.get("voucher_no"),
                company_id=request.user.company_id,
            )
        except JournalVoucher.DoesNotExist:
            return Response({"detail": "Journal voucher not found."}, status=404)
        status = serializer.validated_data.get("status")
        if status == "Cancelled":
            reason = serializer.validated_data.get("reason")
            journal_voucher.cancel(reason=reason)
        else:
            journal_voucher.status = status
            journal_voucher.save()
        return Response({"detail": "Status changed successfully."})


class PartnerPartyViewSet(viewsets.GenericViewSet):
    queryset = Party.objects.all()

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        parties = (
            self.queryset.filter(company_id=request.company_id)
            .order_by("-pk")
            .only("id", "name")
        )
        return Response(PartnerPartyListSerializer(parties, many=True).data)


class PartnerSalesVoucherViewSet(SalesVoucherViewSet):
    def get_serializer_class(self):
        if self.request.META.get("HTTP_SECRET"):
            return PartnerSalesVoucherAccessSerializer
        return super().get_serializer_class()
