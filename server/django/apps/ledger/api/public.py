from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.voucher.models.journal_vouchers import JournalVoucher
from apps.voucher.serializers.journal_voucher import (
    PublicJournalVoucherCreateSerializer,
    PublicJournalVoucherStatusChangeSerializer,
)


class PublicJournalVoucherViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = PublicJournalVoucherCreateSerializer
    queryset = PublicJournalVoucherCreateSerializer.Meta.model.objects.all()

    @action(detail=False, methods=["post"], url_path="change-status")
    def change_status(self, request):
        serializer = PublicJournalVoucherStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        journal_voucher = JournalVoucher.objects.filter(
            voucher_no=serializer.validated_data.get("voucher_no"),
            company_id=request.user.company_id,
        ).first()
        if not journal_voucher:
            return Response({"detail": "Journal Voucher not found"}, status=404)
        journal_voucher.status = serializer.validated_data.get("status")
        journal_voucher.save()
        return Response({"detail": "Status changed successfully"})
