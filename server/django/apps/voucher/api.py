from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from xhtml2pdf import pisa

from apps.ledger.serializers import JournalEntrySerializer, SalesJournalEntrySerializer
from awecount.utils import get_next_voucher_no, link_callback
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.helpers import merge_dicts
from awecount.utils.mixins import DeleteRows, InputChoiceMixin
from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES, STATUSES, MODES, CreditVoucher, CreditVoucherRow, \
    InvoiceDesign, JournalVoucher, JournalVoucherRow, PurchaseVoucher, PurchaseVoucherRow
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditVoucherCreateSerializer, \
    CreditVoucherListSerializer, InvoiceDesignSerializer, \
    SaleVoucherRowCreditNoteOptionsSerializer, JournalVoucherListSerializer, \
    JournalVoucherCreateSerializer, PurchaseVoucherCreateSerializer, PurchaseVoucherListSerializer, \
    SalesDiscountSerializer, PurchaseDiscountSerializer, SalesVoucherDetailSerializer, SalesBookSerializer


class SalesVoucherViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = SalesVoucher.objects.all()
    serializer_class = SalesVoucherCreateSerializer
    model = SalesVoucher
    row = SalesVoucherRow

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
        sale_voucher = self.get_object()
        if sale_voucher.is_issued():
            if not request.company.enable_sales_voucher_update:
                raise APIException({'non_field_errors': ['Issued sales invoices can\'t be updated']})
            _model_name = self.get_queryset().model.__name__
            permission = '{}IssuedModify'.format(_model_name)
            modules = request.user.role.modules
            if permission not in modules:
                raise APIException({'non_field_errors': ['User do not have permission to issue voucher']})
        return super(SalesVoucherViewSet, self).update(request, *args, **kwargs)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        sale_voucher = get_object_or_404(SalesVoucher, pk=pk)
        journals = sale_voucher.journal_entries()
        return Response(SalesJournalEntrySerializer(journals, many=True).data)

    @action(detail=True)
    def details(self, request, pk):
        return Response(SalesVoucherDetailSerializer(self.get_object()).data)

    def get_defaults(self, request=None):
        data = {
            'fields': {
                'can_update_issued': request.company.enable_sales_voucher_update
            }
        }
        return data

    def get_create_defaults(self, request=None):
        voucher_no = get_next_voucher_no(SalesVoucher, request.company_id)
        data = {
            'fields': {
                'voucher_no': voucher_no,
            }
        }
        return data

    @action(detail=False)
    def options(self, request):
        discount_type = {
            "Percent": "%",
            "Amount": "/-",
        }
        types = [dict(value=type[0], text=discount_type.get(type[1])) for type in DISCOUNT_TYPES]
        statuses = [dict(value=status[0], text=status[1]) for status in STATUSES]
        modes = [dict(value=mode[0], text=mode[1]) for mode in MODES]
        types.insert(0, {"value": None, "text": '---'})
        statuses.insert(0, {"value": None, "text": '---'})
        # modes.insert(0, {"value": None, "text": '---'})
        return Response({
            'discount_types': types,
            'statues': statuses,
            'modes': modes
        })

    @action(detail=True)
    def pdf(self, request, pk):
        sale_voucher = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        template = get_template('sale_voucher_pdf.html')
        html = template.render({'object': sale_voucher})

        # create a pdf
        pisaStatus = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        if pisaStatus.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response

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

    @action(detail=True, methods=['POST'], url_path="log-print")
    def log_print(self, request, pk):
        sale_voucher = self.get_object()
        sale_voucher.print_count += 1
        sale_voucher.save()
        return Response({'print_count': sale_voucher.print_count})

    @action(detail=True)
    def rows(self, request, pk):
        sale_voucher = self.get_object()
        sale_voucher_rows = sale_voucher.rows.all()
        data = SaleVoucherRowCreditNoteOptionsSerializer(sale_voucher_rows, many=True).data
        return Response(data)


class PurchaseVoucherViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = PurchaseVoucher.objects.all()
    serializer_class = PurchaseVoucherCreateSerializer
    model = PurchaseVoucher
    row = PurchaseVoucherRow

    def get_queryset(self):
        queryset = super(PurchaseVoucherViewSet, self).get_queryset()
        return queryset.order_by('-pk')

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ('choices',):
            return PurchaseVoucherListSerializer
        return PurchaseVoucherCreateSerializer

    @action(detail=False)
    def options(self, request):
        discount_type = {
            "Percent": "%",
            "Amount": "/-",
        }
        types = [dict(value=type[0], text=discount_type.get(type[1])) for type in DISCOUNT_TYPES]
        tax_choices = [dict(value=tax_choice[0], text=tax_choice[1]) for tax_choice in PurchaseVoucher.tax_choices]
        types.insert(0, {"value": None, "text": '---'})

        tax_choices.insert(0, {"value": None, "text": '---'})
        return Response({
            'discount_types': types,
            'tax_choices': tax_choices,
        })

    @action(detail=True)
    def rows(self, request, pk):
        sale_voucher = self.get_object()
        sale_voucher_rows = sale_voucher.rows.all()
        data = SaleVoucherRowCreditNoteOptionsSerializer(sale_voucher_rows, many=True).data
        return Response(data)

    @action(detail=True, url_path='journal-entries')
    def journal_entries(self, request, pk):
        purchase_voucher = get_object_or_404(PurchaseVoucher, pk=pk)
        journals = purchase_voucher.journal_entries()
        return Response(SalesJournalEntrySerializer(journals, many=True).data)


class CreditVoucherViewSet(DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = CreditVoucher.objects.all()
    serializer_class = CreditVoucherCreateSerializer
    model = CreditVoucher
    row = CreditVoucherRow

    def get_queryset(self):
        queryset = super(CreditVoucherViewSet, self).get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CreditVoucherListSerializer
        return CreditVoucherCreateSerializer

    @action(detail=False)
    def get_next_no(self, request):
        voucher_no = get_next_voucher_no(CreditVoucher, request.company.id)
        return Response({'voucher_no': voucher_no})


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

    def get_queryset(self):
        qs = super(SalesBookViewSet, self).get_queryset()
        return qs.order_by('-pk')
