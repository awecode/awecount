from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ledger.serializers.public import (
    PublicJournalVoucherCreateResponseSerializer,
    PublicJournalVoucherCreateSerializer,
    PublicJournalVoucherStatusChangeSerializer,
)
from apps.voucher.models.journal_vouchers import JournalVoucher


class PublicJournalVoucherViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = PublicJournalVoucherCreateSerializer
    queryset = PublicJournalVoucherCreateSerializer.Meta.model.objects.all()

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        serializer = PublicJournalVoucherCreateResponseSerializer(data=res.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="change-status")
    def change_status(self, request):
        serializer = PublicJournalVoucherStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            journal_voucher = JournalVoucher.objects.get(
                voucher_no=serializer.validated_data.get("voucher_no"),
                company_id=request.user.company_id,
            )
        except JournalVoucher.DoesNotExist:
            return Response({"detail": "Journal Voucher not found."}, status=404)
        journal_voucher.status = serializer.validated_data.get("status")
        journal_voucher.save()
        return Response({"detail": "Status changed successfully."})
