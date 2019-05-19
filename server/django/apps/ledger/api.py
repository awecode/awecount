from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from apps.voucher.models import SalesVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from .models import Account
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class PartyViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer

    @action(detail=True)
    def sale_vouchers(self, request, pk=None):
        sale_vouchers = SalesVoucher.objects.filter(party_id=pk)
        data = SaleVoucherOptionsSerializer(sale_vouchers, many=True).data
        return Response(data)


class CategoryViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = CategorySerializer


class AccountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('code', 'name',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'])
    def project_fy_cr_ledger_choices(self, request, pk=None):
        instance = self.get_object()
        data = AccountSerializer(instance, many=True).data
        return Response(data)
