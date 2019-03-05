import json
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES, STATUSES, MODES, CreditVoucher, CreditVoucherRow, \
    ChequeVoucher
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditVoucherCreateSerializer, \
    CreditVoucherListSerializer, ChequeVoucherSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.mixins import DeleteRows, InputChoiceMixin


class SalesVoucherViewSet(InputChoiceMixin, DeleteRows, viewsets.ModelViewSet):
    queryset = SalesVoucher.objects.all()
    model = SalesVoucher
    row = SalesVoucherRow

    def get_queryset(self):
        return SalesVoucher.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return SalesVoucherListSerializer
        return SalesVoucherCreateSerializer

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(SalesVoucher, request.company.id)
        return Response({'voucher_no': voucher_no})

    @action(detail=False)
    def options(self, request):
        return Response({
            'discount_types': [dict(value=type[0], text=type[1]) for type in DISCOUNT_TYPES],
            'statues': [dict(value=status[0], text=status[1]) for status in STATUSES],
            'modes': [dict(value=mode[0], text=mode[1]) for mode in MODES]
        })


class CreditVoucherViewSet(DeleteRows, viewsets.ModelViewSet):
    queryset = CreditVoucher.objects.all()
    model = CreditVoucher
    row = CreditVoucherRow

    def get_queryset(self):
        return CreditVoucher.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CreditVoucherListSerializer
        return CreditVoucherCreateSerializer

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(CreditVoucher, request.company.id)
        return Response({'voucher_no': voucher_no})


class ChequeVoucherViewSet(viewsets.ModelViewSet):
    queryset = ChequeVoucher.objects.all()
    serializer_class = ChequeVoucherSerializer

    def get_queryset(self):
        return ChequeVoucher.objects.all()
