from rest_framework import mixins, viewsets

from apps.voucher.serializers.journal_voucher import (
    PublicJournalVoucherCreateSerializer,
)


class PublicJournalVoucherViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = PublicJournalVoucherCreateSerializer
    queryset = PublicJournalVoucherCreateSerializer.Meta.model.objects.all()