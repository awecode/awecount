import json
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer
from awecount.utils import get_next_voucher_no


class SalesVoucherViewSet(viewsets.ModelViewSet):
    queryset = SalesVoucher.objects.all()
    model = SalesVoucher
    row = SalesVoucherRow

    def get_queryset(self):
        return SalesVoucher.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SalesVoucherListSerializer
        return SalesVoucherCreateSerializer

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(SalesVoucher, 'voucher_no')
        return Response({'voucher_no': voucher_no})

    @action(detail=False)
    def options(self, request):
        return Response({
            'discount_types': [dict(value=type[0], text=type[1]) for type in DISCOUNT_TYPES]
        })
