from django.db.models import Prefetch, Q

from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import filters as rf_filters

from apps.aggregator.views import qs_to_xls
from apps.bank.models import BankAccount
from apps.bank.serializers import BankAccountSerializer
from apps.ledger.models import Party, Account
from apps.ledger.serializers import SalesJournalEntrySerializer, PartyMinSerializer, JournalEntriesSerializer, \
    AccountSerializer
from apps.product.models import Unit, Item
from apps.product.serializers import ItemSalesSerializer, ItemPurchaseSerializer, ItemPOSSerializer
from apps.tax.models import TaxScheme
from apps.tax.serializers import TaxSchemeMinSerializer
from apps.users.serializers import FiscalYearSerializer
from apps.voucher.filters import SalesVoucherFilterSet, PurchaseVoucherFilterSet, CreditNoteFilterSet, \
    SalesDiscountFilterSet, DebitNoteFilterSet, PurchaseDiscountFilterSet
from apps.voucher.models import SalesAgent

from apps.voucher.resources import SalesVoucherResource, SalesVoucherRowResource, PurchaseVoucherResource, \
    PurchaseVoucherRowResource, CreditNoteResource, CreditNoteRowResource, DebitNoteResource, DebitNoteRowResource
from apps.voucher.serializers.debit_note import DebitNoteCreateSerializer, DebitNoteListSerializer, \
    DebitNoteDetailSerializer
from apps.voucher.serializers.voucher_settings import SalesCreateSettingSerializer, PurchaseCreateSettingSerializer, \
    SalesUpdateSettingSerializer, PurchaseUpdateSettingSerializer, PurchaseSettingSerializer, SalesSettingsSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.mixins import DeleteRows, InputChoiceMixin
from .models import SalesVoucher, SalesVoucherRow, CreditNote, CreditNoteRow, \
    InvoiceDesign, JournalVoucher, JournalVoucherRow, PurchaseVoucher, PurchaseVoucherRow, SalesDiscount, \
    PurchaseDiscount, \
    DebitNote, DebitNoteRow
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditNoteCreateSerializer, \
    CreditNoteListSerializer, InvoiceDesignSerializer, \
    JournalVoucherListSerializer, \
    JournalVoucherCreateSerializer, PurchaseVoucherCreateSerializer, PurchaseVoucherListSerializer, \
    SalesDiscountSerializer, PurchaseDiscountSerializer, SalesVoucherDetailSerializer, SalesBookSerializer, \
    CreditNoteDetailSerializer, SalesDiscountMinSerializer, PurchaseVoucherDetailSerializer, PurchaseBookSerializer, \
    SalesAgentSerializer, SalesVoucherRowSerializer, SalesRowSerializer


class SalesVoucherViewSet(InputChoiceMixin, DeleteRows, CRULViewSet):
    queryset = SalesVoucher.objects.all()
    serializer_class = SalesVoucherCreateSerializer
    model = SalesVoucher
    row = SalesVoucherRow
    collections = [
        ('parties', Party, PartyMinSerializer),
        ('units', Unit),
        ('discounts', SalesDiscount, SalesDiscountMinSerializer),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('items', Item.objects.filter(can_be_sold=True), ItemSalesSerializer),
    ]

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]

    filterset_class = SalesVoucherFilterSet

    search_fields = ['voucher_no', 'party__name', 'remarks', 'total_amount', 'party__tax_registration_number',
                     'customer_name',
                     'rows__item__name']

    def get_collections(self, request=None):
        sales_agent_tuple = ('sales_agents', SalesAgent)
        if request.company.enable_sales_agents and sales_agent_tuple not in self.collections:
            # noinspection PyTypeChecker
            self.collections.append(sales_agent_tuple)
        return super().get_collections(request)

    def get_queryset(self, **kwargs):
        qs = super(SalesVoucherViewSet, self).get_queryset()
        if self.action == 'list':
            qs = qs.select_related('party')
        return qs.order_by('-pk')

    def get_serializer_class(self):
        if self.action in ('choices', 'list'):
            return SalesVoucherListSerializer
        return SalesVoucherCreateSerializer

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_issued():
            if not request.company.enable_sales_invoice_update:
                raise APIException({'detail': 'Issued sales invoices can\'t be updated'})
            permission = '{}IssuedModify'.format(self.get_queryset().model.__name__)
            self.request.user.check_perm(permission)
        return super().update(request, *args, **kwargs)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        sale_voucher = get_object_or_404(SalesVoucher, pk=pk)
        journals = sale_voucher.journal_entries()
        return Response(SalesJournalEntrySerializer(journals, many=True).data)

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     SalesVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                                  'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        data = SalesVoucherDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_sales_invoice_update
        return Response(data)

    def get_defaults(self, request=None):
        return {
            'options': {
                'enable_sales_agents': request.company.enable_sales_agents
            },
        }

    def get_create_defaults(self, request=None):
        data = SalesCreateSettingSerializer(request.company.sales_setting).data
        data['options']['voucher_no'] = get_next_voucher_no(SalesVoucher, request.company_id)
        return data

    def get_update_defaults(self, request=None):
        data = SalesUpdateSettingSerializer(request.company.sales_setting).data
        data['options']['can_update_issued'] = request.company.enable_sales_invoice_update
        obj = self.get_object()
        if not obj.voucher_no:
            data['options']['voucher_no'] = get_next_voucher_no(SalesVoucher, request.company_id)
        return data

    @action(detail=True, methods=['POST'])
    def mark_as_paid(self, request, pk):
        sale_voucher = self.get_object()
        try:
            sale_voucher.mark_as_resolved(status='Paid')
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        sale_voucher = self.get_object()
        try:
            sale_voucher.cancel()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'], url_path='log-print')
    def log_print(self, request, pk):
        sale_voucher = self.get_object()
        sale_voucher.print_count += 1
        sale_voucher.save()
        return Response({'print_count': sale_voucher.print_count})

    @action(detail=False, url_path='by-voucher-no')
    def by_voucher_no(self, request):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     SalesVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                                  'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(
            SalesVoucherDetailSerializer(get_object_or_404(voucher_no=request.query_params.get('invoice_no'),
                                                           fiscal_year_id=request.query_params.get('fiscal_year'),
                                                           queryset=qs)).data)

    @action(detail=False)
    def export(self, request):
        params = [
            ('Invoices', self.get_queryset(), SalesVoucherResource),
            ('Sales Rows', SalesVoucherRow.objects.filter(voucher__company_id=request.company_id),
             SalesVoucherRowResource),
        ]
        return qs_to_xls(params)


class POSViewSet(DeleteRows, CRULViewSet):
    queryset = SalesVoucher.objects.all()
    serializer_class = SalesVoucherCreateSerializer
    model = SalesVoucher
    ITEMS_SIZE = 1
    collections = [
        ('parties', Party.objects.only('name', 'address', 'logo', 'tax_registration_number'), PartyMinSerializer),
        ('units', Unit.objects.only('name', 'short_name')),
        ('discounts', SalesDiscount.objects.only('name', 'type', 'value'), SalesDiscountMinSerializer),
        ('bank_accounts', BankAccount.objects.only('short_name', 'bank_name')),
        ('tax_schemes', TaxScheme.objects.only('name', 'short_name', 'rate'), TaxSchemeMinSerializer),
    ]

    def get_collections(self, request=None):
        data = super().get_collections(request)

        # self.paginator.page_size = self.ITEMS_SIZE
        # items = Item.objects.filter(can_be_sold=True)
        # page = self.paginate_queryset(items)
        # serializer = ItemPOSSerializer(page, many=True)
        # data['items'] = self.paginator.get_response_data(serializer.data)

        qs = Item.objects.filter(can_be_sold=True, company_id=request.company_id).only(
            'name', 'unit_id', 'selling_price', 'tax_scheme_id', 'code')[:self.ITEMS_SIZE]
        data['items'] = ItemPOSSerializer(qs, many=True).data

        return data


class PurchaseVoucherViewSet(InputChoiceMixin, DeleteRows, CRULViewSet):
    serializer_class = PurchaseVoucherCreateSerializer
    model = PurchaseVoucher
    row = PurchaseVoucherRow

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'party__name', 'remarks', 'total_amount', 'party__tax_registration_number',
                     'rows__item__name']
    filterset_class = PurchaseVoucherFilterSet

    collections = (
        ('parties', Party, PartyMinSerializer),
        ('discounts', PurchaseDiscount, PurchaseDiscountSerializer),
        ('units', Unit),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('bank_accounts', BankAccount, BankAccountSerializer),
        ('items',
         Item.objects.filter(
             Q(can_be_purchased=True) | Q(direct_expense=True) | Q(indirect_expense=True) | Q(fixed_asset=True)),
         ItemPurchaseSerializer),
    )

    def get_create_defaults(self, request=None):
        return PurchaseCreateSettingSerializer(request.company.purchase_setting).data

    def get_update_defaults(self, request=None):
        data = PurchaseUpdateSettingSerializer(request.company.purchase_setting).data
        obj = self.get_object()
        if not obj.voucher_no:
            data['options']['voucher_no'] = get_next_voucher_no(PurchaseVoucher, request.company_id)
        return data

    def get_queryset(self, **kwargs):
        queryset = super(PurchaseVoucherViewSet, self).get_queryset()
        return queryset.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return PurchaseVoucherListSerializer
        return PurchaseVoucherCreateSerializer

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     PurchaseVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                                     'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(PurchaseVoucherDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        purchase_voucher = get_object_or_404(PurchaseVoucher, pk=pk)
        journals = purchase_voucher.journal_entries()
        return Response(SalesJournalEntrySerializer(journals, many=True).data)

    @action(detail=False, url_path='by-voucher-no')
    def by_voucher_no(self, request):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     PurchaseVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                                     'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(
            PurchaseVoucherDetailSerializer(get_object_or_404(voucher_no=request.query_params.get('invoice_no'),
                                                              party_id=request.query_params.get('party'),
                                                              fiscal_year_id=request.query_params.get('fiscal_year'),
                                                              queryset=qs)).data)

    @action(detail=True, methods=['POST'])
    def mark_as_paid(self, request, pk):
        purchase_voucher = self.get_object()
        try:
            purchase_voucher.mark_as_resolved(status='Paid')
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        purchase_voucher = self.get_object()
        try:
            purchase_voucher.cancel()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=False)
    def export(self, request):
        params = [
            ('Invoices', self.get_queryset(), PurchaseVoucherResource),
            ('Purchase Rows', PurchaseVoucherRow.objects.filter(voucher__company_id=request.company_id),
             PurchaseVoucherRowResource),
        ]
        return qs_to_xls(params)


class CreditNoteViewSet(DeleteRows, CRULViewSet):
    serializer_class = CreditNoteCreateSerializer
    model = CreditNote
    row = CreditNoteRow

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'party__name', 'remarks', 'total_amount', 'party__tax_registration_number',
                     'rows__item__name']
    filterset_class = CreditNoteFilterSet

    collections = (
        ('discounts', SalesDiscount, SalesDiscountSerializer),
        ('units', Unit),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('bank_accounts', BankAccount, BankAccountSerializer),
        ('items', Item.objects.filter(can_be_sold=True), ItemSalesSerializer),
    )

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_issued():
            if not request.company.enable_credit_note_update:
                raise APIException({'detail': 'Issued credit notes can\'t be updated'})
            permission = '{}IssuedModify'.format(self.get_queryset().model.__name__)
            self.request.user.check_perm(permission)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return CreditNoteListSerializer
        return CreditNoteCreateSerializer

    def get_defaults(self, request=None):
        data = {
            'options': {
                'fiscal_years': FiscalYearSerializer(request.company.get_fiscal_years(), many=True).data
            },
            'fields': {
                'can_update_issued': request.company.enable_credit_note_update
            }
        }
        return data

    def get_create_defaults(self, request=None):
        options = SalesCreateSettingSerializer(request.company.sales_setting).data
        options['voucher_no'] = get_next_voucher_no(CreditNote, request.company_id)
        return {
            'options': options
        }

    def get_update_defaults(self, request=None):
        options = SalesUpdateSettingSerializer(request.company.sales_setting).data

        obj = self.get_object()
        invoice_objs = []
        for inv in obj.invoices.all():
            invoice_objs.append({'id': inv.id, 'voucher_no': inv.voucher_no})
        options['sales_invoice_objs'] = invoice_objs
        if not obj.voucher_no:
            options['voucher_no'] = get_next_voucher_no(SalesVoucher, request.company_id)

        return {
            'options': options
        }

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     CreditNoteRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                                'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        data = CreditNoteDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_credit_note_update
        return Response(data)

    @action(detail=True, methods=['POST'])
    def mark_as_resolved(self, request, pk):
        obj = self.get_object()
        try:
            obj.mark_as_resolved()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        obj = self.get_object()
        try:
            obj.cancel()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'], url_path='log-print')
    def log_print(self, request, pk):
        obj = self.get_object()
        obj.print_count += 1
        obj.save()
        return Response({'print_count': obj.print_count})

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        credit_note = get_object_or_404(CreditNote, pk=pk)
        journals = credit_note.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)

    @action(detail=False)
    def export(self, request):
        params = [
            ('Invoices', self.get_queryset(), CreditNoteResource),
            ('Credit Note Rows', CreditNoteRow.objects.filter(voucher__company_id=request.company_id),
             CreditNoteRowResource),
        ]
        return qs_to_xls(params)


class DebitNoteViewSet(DeleteRows, CRULViewSet):
    serializer_class = DebitNoteCreateSerializer
    model = DebitNote
    row = DebitNoteRow

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['voucher_no', 'party__name', 'remarks', 'total_amount', 'party__tax_registration_number',
                     'rows__item__name']
    filterset_class = DebitNoteFilterSet

    collections = (
        ('discounts', PurchaseDiscount, PurchaseDiscountSerializer),
        ('units', Unit),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('bank_accounts', BankAccount, BankAccountSerializer),
        ('items', Item.objects.filter(can_be_purchased=True), ItemPurchaseSerializer),
    )

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_issued():
            if not request.company.enable_credit_note_update:
                raise APIException({'detail': 'Issued debit notes can\'t be updated'})
            permission = '{}IssuedModify'.format(self.get_queryset().model.__name__)
            self.request.user.check_perm(permission)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return DebitNoteListSerializer
        return DebitNoteCreateSerializer

    def get_defaults(self, request=None):
        data = {
            'options': {
                'fiscal_years': FiscalYearSerializer(request.company.get_fiscal_years(), many=True).data
            },
            'fields': {
                'can_update_issued': request.company.enable_debit_note_update
            }
        }
        return data

    def get_create_defaults(self, request=None):
        options = PurchaseCreateSettingSerializer(request.company.purchase_setting).data
        options['voucher_no'] = get_next_voucher_no(DebitNote, request.company_id)
        return {
            'options': options
        }

    def get_update_defaults(self, request=None):
        options = PurchaseUpdateSettingSerializer(request.company.purchase_setting).data
        obj = self.get_object()
        invoice_objs = []
        for inv in obj.invoices.all():
            invoice_objs.append({'id': inv.id, 'voucher_no': inv.voucher_no})
        options['purchase_invoice_objs'] = invoice_objs

        if not obj.voucher_no:
            options['voucher_no'] = get_next_voucher_no(PurchaseVoucher, request.company_id)
        return {
            'options': options
        }

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     DebitNoteRow.objects.all().select_related('item', 'unit', 'discount_obj',
                                                               'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        data = DebitNoteDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data
        data['can_update_issued'] = request.company.enable_debit_note_update
        return Response(data)

    @action(detail=True, methods=['POST'])
    def mark_as_resolved(self, request, pk):
        obj = self.get_object()
        try:
            obj.mark_as_resolved()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk):
        obj = self.get_object()
        try:
            obj.cancel()
            return Response({})
        except Exception as e:
            raise APIException(str(e))

    @action(detail=True, methods=['POST'], url_path='log-print')
    def log_print(self, request, pk):
        obj = self.get_object()
        obj.print_count += 1
        obj.save()
        return Response({'print_count': obj.print_count})

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        debit_note = get_object_or_404(DebitNote, pk=pk)
        journals = debit_note.journal_entries()
        return Response(JournalEntriesSerializer(journals, many=True).data)

    @action(detail=False)
    def export(self, request):
        params = [
            ('Invoices', self.get_queryset(), DebitNoteResource),
            ('Debit Note Rows', DebitNoteRow.objects.filter(voucher__company_id=request.company_id),
             DebitNoteRowResource),
        ]
        return qs_to_xls(params)


class JournalVoucherViewSet(DeleteRows, CRULViewSet):
    queryset = JournalVoucher.objects.prefetch_related(Prefetch('rows',
                                                                queryset=JournalVoucherRow.objects.order_by('-type',
                                                                                                            'id')))
    serializer_class = JournalVoucherCreateSerializer
    model = JournalVoucher
    row = JournalVoucherRow
    collections = (
        ('accounts', Account, AccountSerializer),

    )

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return JournalVoucherListSerializer
        return JournalVoucherCreateSerializer

    def get_create_defaults(self, request=None):
        voucher_no = get_next_voucher_no(JournalVoucher, request.company_id)
        data = {
            'fields': {
                'voucher_no': voucher_no,
            }
        }
        return data

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(JournalVoucher, request.company_id)
        return Response({'voucher_no': voucher_no})


class InvoiceDesignViewSet(CRULViewSet):
    queryset = InvoiceDesign.objects.all()
    serializer_class = InvoiceDesignSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data._mutable = True
        design = request.data.pop('design', None)
        serializer = InvoiceDesignSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        if 'design' in request.FILES:
            instance.refresh_from_db()
            instance.design = request.FILES.get('design')
            instance.save()
        return Response(serializer.validated_data)

    @action(detail=True)
    def company_invoice(self, request, pk):
        data = {}
        try:
            invoice = InvoiceDesign.objects.get(company_id=pk)
            data = self.serializer_class(invoice).data
        except InvoiceDesign.DoesNotExist:
            pass
        return Response(data)


class SalesDiscountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = SalesDiscountSerializer

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['name', ]
    filterset_class = SalesDiscountFilterSet


class PurchaseDiscountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = PurchaseDiscountSerializer

    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter]
    search_fields = ['name', ]
    filterset_class = PurchaseDiscountFilterSet


class SalesBookViewSet(CRULViewSet):
    serializer_class = SalesBookSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SalesVoucherFilterSet

    def get_queryset(self, **kwargs):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     SalesVoucherRow.objects.all().select_related('discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'party')
        return qs.order_by('-pk')


class SalesRowViewSet(CRULViewSet):
    serializer_class = SalesRowSerializer

    def get_queryset(self, **kwargs):
        qs = SalesVoucherRow.objects.filter(voucher__company_id=self.request.company_id).select_related('item',
                                                                                                        'discount_obj',
                                                                                                        'tax_scheme',
                                                                                                        'voucher',
                                                                                                        'unit')
        return qs.order_by('-pk')


class PurchaseBookViewSet(CRULViewSet):
    serializer_class = PurchaseBookSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PurchaseVoucherFilterSet

    def get_queryset(self, **kwargs):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     PurchaseVoucherRow.objects.all().select_related('discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'party')
        return qs.order_by('-pk')


class SalesAgentViewSet(CRULViewSet):
    serializer_class = SalesAgentSerializer


class PurchaseSettingsViewSet(CRULViewSet):
    serializer_class = PurchaseSettingSerializer
    collections = (
        ('bank_accounts', BankAccount, BankAccountSerializer),
    )

    def get_defaults(self, request=None):
        p_setting = self.request.company.purchase_setting

        data = {
            'fields': PurchaseSettingSerializer(p_setting).data
        }
        return data


class SalesSettingsViewSet(CRULViewSet):
    serializer_class = SalesSettingsSerializer
    collections = (
        ('bank_accounts', BankAccount, BankAccountSerializer),
    )

    def get_defaults(self, request=None):
        s_setting = self.request.company.sales_setting

        data = {
            'fields': SalesSettingsSerializer(s_setting).data
        }
        return data
