from datetime import datetime
from django.db.models import Q
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from apps.voucher.models import SalesVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from .models import Account, JournalEntry
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer, \
    JournalEntrySerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin, JournalEntriesMixin


class PartyViewSet(InputChoiceMixin, JournalEntriesMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer
    account_keys = ['supplier_account', 'customer_account']

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

    def get_queryset(self):
        # TODO View transaction with or without cr or dr amount
        queryset = Account.objects.filter(Q(current_dr__gt=0)|Q(current_cr__gt=0))
        return queryset

    def get_discount_account(self, category_name):
        queryset = self.get_queryset()
        queryset = queryset.filter(category__name=category_name)
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    @action(detail=False)
    def discount_allowed(self, request):
        data = self.get_discount_account('Discount Expenses')
        return Response(data)

    @action(detail=False)
    def discount_received(self, request):
        data = self.get_discount_account('Discount Income')
        return Response(data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'])
    def project_fy_cr_ledger_choices(self, request, pk=None):
        instance = self.get_object()
        data = AccountSerializer(instance, many=True).data
        return Response(data)

    @action(detail=True, methods=['get'], url_path='journal-entries')
    def journal_entries(self, request, pk=None):
        param = request.GET
        start_date = param.get('start_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = param.get('end_date')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        obj = self.get_object()
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()
        if start_date == end_date:
            entries = entries.filter(date=start_date)
        else:
            entries = entries.filter(date__range=[start_date, end_date])
        data = JournalEntrySerializer(entries, context={'account': obj}, many=True).data
        return Response(data)
