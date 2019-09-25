from datetime import datetime
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.response import Response

from apps.voucher.models import SalesVoucher
from apps.voucher.serializers import SaleVoucherOptionsSerializer
from .models import Account, JournalEntry, Category
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer, CategorySerializer, \
    JournalEntrySerializer
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import InputChoiceMixin, JournalEntriesMixin


class PartyViewSet(InputChoiceMixin, JournalEntriesMixin, CRULViewSet):
    serializer_class = PartySerializer
    account_keys = ['supplier_account', 'customer_account']
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('name', 'tax_registration_number', 'contact_no', 'address',)

    @action(detail=True)
    def sales_vouchers(self, request, pk=None):
        sales_vouchers = SalesVoucher.objects.filter(party_id=pk)
        data = SaleVoucherOptionsSerializer(sales_vouchers, many=True).data
        return Response(data)


class CategoryViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = CategorySerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)
    collections = (
        ('categories', Category, CategorySerializer),
    )


class AccountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = AccountSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)

    def get_queryset(self):
        # TODO View transaction with or without cr or dr amount
        # queryset = Account.objects.filter(Q(current_dr__gt=0)|Q(current_cr__gt=0), company=self.request.company)
        queryset = Account.objects.filter(company=self.request.company)
        return queryset

    def get_accounts_by_category_name(self, category_name):
        queryset = self.get_queryset()
        queryset = queryset.filter(category__name=category_name, company=self.request.company)
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'], url_path='journal-entries')
    def journal_entries(self, request, pk=None):
        param = request.GET
        start_date = param.get('start_date')
        end_date = param.get('end_date')
        obj = self.get_object()
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()

        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if start_date == end_date:
                entries = entries.filter(date=start_date)
            else:
                entries = entries.filter(date__range=[start_date, end_date])

        data = JournalEntrySerializer(entries, context={'account': obj}, many=True).data
        return Response(data)
