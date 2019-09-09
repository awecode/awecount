from django.db.models import Prefetch

from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.bank.models import BankAccount
from apps.bank.serializers import BankAccountSerializer
from apps.ledger.models import Party
from apps.ledger.serializers import SalesJournalEntrySerializer, PartyMinSerializer
from apps.product.models import Unit, Item
from apps.product.serializers import ItemSalesSerializer
from apps.tax.models import TaxScheme
from apps.tax.serializers import TaxSchemeMinSerializer
from apps.users.serializers import FiscalYearSerializer
from apps.voucher.filters import SalesVoucherDateFilterSet
from apps.voucher.serializers.debit_note import DebitNoteCreateSerializer, DebitNoteListSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import DeleteRows, InputChoiceMixin
from .models import SalesVoucher, SalesVoucherRow, CreditNote, CreditNoteRow, \
    InvoiceDesign, JournalVoucher, JournalVoucherRow, PurchaseVoucher, PurchaseVoucherRow, SalesDiscount, PurchaseDiscount, \
    DebitNote, DebitNoteRow
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditNoteCreateSerializer, \
    CreditNoteListSerializer, InvoiceDesignSerializer, \
    JournalVoucherListSerializer, \
    JournalVoucherCreateSerializer, PurchaseVoucherCreateSerializer, PurchaseVoucherListSerializer, \
    SalesDiscountSerializer, PurchaseDiscountSerializer, SalesVoucherDetailSerializer, SalesBookSerializer, \
    CreditNoteDetailSerializer, SalesDiscountMinSerializer, PurchaseVoucherDetailSerializer


class SalesVoucherViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = SalesVoucher.objects.all()
    serializer_class = SalesVoucherCreateSerializer
    model = SalesVoucher
    row = SalesVoucherRow
    collections = (
        ('parties', Party.objects.only('name', 'address', 'logo', 'tax_registration_number'), PartyMinSerializer),
        ('units', Unit.objects.only('name', 'short_name')),
        ('discounts', SalesDiscount.objects.only('name', 'type', 'value'), SalesDiscountMinSerializer),
        ('bank_accounts', BankAccount.objects.only('short_name', 'account_number')),
        ('tax_schemes', TaxScheme.objects.only('name', 'short_name', 'rate'), TaxSchemeMinSerializer),
        ('items',
         Item.objects.only('name', 'unit_id', 'selling_price', 'tax_scheme_id', 'code', 'description').filter(can_be_sold=True),
         ItemSalesSerializer),
    )

    def get_queryset(self):
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
            if not request.company.enable_sales_voucher_update:
                raise APIException({'non_field_errors': ['Issued sales invoices can\'t be updated']})
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
                     SalesVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(SalesVoucherDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data)

    def get_defaults(self, request=None):
        data = {
            'fields': {
                'can_update_issued': request.company.enable_sales_voucher_update
            },
        }
        return data

    def get_create_defaults(self, request=None):
        voucher_no = get_next_voucher_no(SalesVoucher, request.company_id)
        data = {
            'options': {
                'voucher_no': voucher_no,
            }
        }
        return data

    def get_update_defaults(self, request=None):
        obj = self.get_object()
        if not obj.voucher_no:
            voucher_no = get_next_voucher_no(SalesVoucher, request.company_id)
            return {
                'options': {
                    'voucher_no': voucher_no,
                }
            }
        return {}

    @action(detail=True, methods=['POST'])
    def mark_as_paid(self, request, pk):
        sale_voucher = self.get_object()
        try:
            sale_voucher.mark_as_paid()
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
                     SalesVoucherRow.objects.all().select_related('item', 'unit', 'discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(SalesVoucherDetailSerializer(get_object_or_404(voucher_no=request.query_params.get('invoice_no'),
                                                                       fiscal_year_id=request.query_params.get('fiscal_year'),
                                                                       queryset=qs)).data)


class PurchaseVoucherViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    serializer_class = PurchaseVoucherCreateSerializer
    model = PurchaseVoucher
    row = PurchaseVoucherRow
    collections = (
        ('parties', Party, PartyMinSerializer),
        ('discounts', PurchaseDiscount, PurchaseDiscountSerializer),
        ('units', Unit),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('bank_accounts', BankAccount, BankAccountSerializer),
        ('items', Item, ItemSalesSerializer),
    )

    def get_create_defaults(self, request=None):
        voucher_no = get_next_voucher_no(SalesVoucher, request.company_id)
        data = {
            'options': {
                'voucher_no': voucher_no,
            }
        }
        return data

    def get_update_defaults(self, request=None):
        obj = self.get_object()
        if not obj.voucher_no:
            voucher_no = get_next_voucher_no(PurchaseVoucher, request.company_id)
            return {
                'options': {
                    'voucher_no': voucher_no,
                }
            }
        return {}

    def get_queryset(self):
        queryset = super(PurchaseVoucherViewSet, self).get_queryset()
        return queryset.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return PurchaseVoucherListSerializer
        return PurchaseVoucherCreateSerializer

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
        return Response(PurchaseVoucherDetailSerializer(get_object_or_404(voucher_no=request.query_params.get('invoice_no'),
                                                                          fiscal_year_id=request.query_params.get('fiscal_year'),
                                                                          queryset=qs)).data)


class CreditNoteViewSet(DeleteRows, CreateListRetrieveUpdateViewSet):
    serializer_class = CreditNoteCreateSerializer
    model = CreditNote
    row = CreditNoteRow
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
        voucher_no = get_next_voucher_no(CreditNote, request.company_id)
        data = {
            'options': {
                'voucher_no': voucher_no,
            }
        }
        return data

    def get_update_defaults(self, request=None):
        obj = self.get_object()
        invoice_objs = []
        for inv in obj.invoices.all():
            invoice_objs.append({'id': inv.id, 'voucher_no': inv.voucher_no})
        data = {
            'options': {
                'sales_invoice_objs': invoice_objs,
            }
        }
        if not obj.voucher_no:
            voucher_no = get_next_voucher_no(SalesVoucher, request.company_id)
            data['options'] = {
                'voucher_no': voucher_no,
            }

        return data

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     CreditNoteRow.objects.all().select_related('item', 'unit', 'discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(CreditNoteDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data)

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


class DebitNoteViewSet(DeleteRows, CreateListRetrieveUpdateViewSet):
    serializer_class = DebitNoteCreateSerializer
    model = DebitNote
    row = DebitNoteRow
    collections = (
        ('discounts', PurchaseDiscount, PurchaseDiscountSerializer),
        ('units', Unit),
        ('bank_accounts', BankAccount),
        ('tax_schemes', TaxScheme, TaxSchemeMinSerializer),
        ('bank_accounts', BankAccount, BankAccountSerializer),
        ('items', Item.objects.filter(can_be_purchased=True), ItemSalesSerializer),
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
            return DebitNoteListSerializer
        return DebitNoteCreateSerializer

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
        voucher_no = get_next_voucher_no(DebitNote, request.company_id)
        data = {
            'options': {
                'voucher_no': voucher_no,
            }
        }
        return data

    def get_update_defaults(self, request=None):
        obj = self.get_object()
        invoice_objs = []
        for inv in obj.invoices.all():
            invoice_objs.append({'id': inv.id, 'voucher_no': inv.voucher_no})
        data = {
            'options': {
                'sales_invoice_objs': invoice_objs,
            }
        }
        if not obj.voucher_no:
            voucher_no = get_next_voucher_no(PurchaseVoucher, request.company_id)
            data['options'] = {
                'voucher_no': voucher_no,
            }

        return data

    @action(detail=True)
    def details(self, request, pk):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     CreditNoteRow.objects.all().select_related('item', 'unit', 'discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'bank_account')
        return Response(CreditNoteDetailSerializer(get_object_or_404(pk=pk, queryset=qs)).data)

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


class JournalVoucherViewSet(DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = JournalVoucher.objects.prefetch_related(Prefetch('rows',
                                                                queryset=JournalVoucherRow.objects.order_by('-type', 'id')))
    serializer_class = JournalVoucherCreateSerializer
    model = JournalVoucher
    row = JournalVoucherRow

    def get_queryset(self):
        queryset = super(JournalVoucherViewSet, self).get_queryset()
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
    def options(self, request):
        statues = [dict(value=status[0], text=status[1]) for status in JournalVoucher.statuses]
        statues.insert(0, {"value": None, "text": '---'})
        return Response({
            'statues': statues,
        })

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(JournalVoucher, request.company.id)
        return Response({'voucher_no': voucher_no})


class InvoiceDesignViewSet(CreateListRetrieveUpdateViewSet):
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


class SalesDiscountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = SalesDiscountSerializer


class PurchaseDiscountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = PurchaseDiscountSerializer


class SalesBookViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = SalesBookSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SalesVoucherDateFilterSet

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related(
            Prefetch('rows',
                     SalesVoucherRow.objects.all().select_related('discount_obj', 'tax_scheme'))).select_related(
            'discount_obj', 'party')
        return qs.order_by('-pk')
