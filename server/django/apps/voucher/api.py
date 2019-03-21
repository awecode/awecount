import json
import cv2
import re
from django.http import HttpResponse
from django.template.loader import render_to_string
from fpdf import FPDF, HTMLMixin
from matplotlib import pyplot as plt
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.nepdate import ad2bs, string_from_tuple
from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES, STATUSES, MODES, CreditVoucher, CreditVoucherRow, \
    ChequeVoucher, BankBranch, InvoiceDesign, BankAccount
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditVoucherCreateSerializer, \
    CreditVoucherListSerializer, ChequeVoucherSerializer, BankBranchSerializer, InvoiceDesignSerializer, \
    BankAccountSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.mixins import DeleteRows, InputChoiceMixin


class GenerateInvoice:
    def __init__(self, startY, default_font_size):
        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.add_page()
        self.pdf.set_margins(20, 10, 20)
        self.currentY = startY
        self.pdf.set_y(startY)
        self.default_font_size = default_font_size
        self.pdf.set_font('Arial', '', default_font_size)

    def move_with(self, value):
        self.currentY += value
        self.pdf.set_y(self.currentY)

    def tab(self, padding):
        self.pdf.cell(padding)

    def text(self, text, width=200, height=50, font_size=12, font_type='', align='L'):
        self.pdf.set_font('Arial', font_type, font_size)
        self.pdf.cell(width, height, text, 0, 0, align)

    def draw_line(self):
        self.pdf.line(20, 45, 190, 45)

    def output(self):
        return self.pdf.output(dest='S').encode('latin-1')


class SalesVoucherViewSet(InputChoiceMixin, DeleteRows, CreateListRetrieveUpdateViewSet):
    queryset = SalesVoucher.objects.all()
    serializer_class = SalesVoucherCreateSerializer
    model = SalesVoucher
    row = SalesVoucherRow

    def get_queryset(self):
        queryset = super(SalesVoucherViewSet, self).get_queryset()
        return queryset.order_by('-pk')

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
        discount_type = {
            "Percent": "%",
            "Amount": "/-",
        }
        types = [dict(value=type[0], text=discount_type.get(type[1])) for type in DISCOUNT_TYPES]
        statues = [dict(value=status[0], text=status[1]) for status in STATUSES]
        modes = [dict(value=mode[0], text=mode[1]) for mode in MODES]
        types.insert(0, {"value": None, "text": '---'})
        statues.insert(0, {"value": None, "text": '---'})
        # modes.insert(0, {"value": None, "text": '---'})
        return Response({
            'discount_types': types,
            'statues': statues,
            'modes': modes
        })

    @action(detail=True)
    def pdf(self, request, pk):
        sale_voucher = self.get_object()
        company = request.company
        pdf = GenerateInvoice(startY=40, default_font_size=12)
        horizontal_width = 170
        pdf.text('TAX INVOICE', horizontal_width, 5, font_type='B', align='C', font_size=16)
        pdf.draw_line()
        pdf.move_with(10)
        text_padding = 25
        value_width = 30
        date = sale_voucher.transaction_date.strftime('%m-%b-%Y')
        pdf.text('Date', text_padding, 5, align='L')
        pdf.text(': %s' % date, value_width, 5, align='L')
        pdf.text('VAT Reg No.: %s' % company.tax_registration_number, horizontal_width - text_padding - value_width, 5,
                 font_type='B', align='R')
        pdf.move_with(5)
        bs_date = string_from_tuple(ad2bs(sale_voucher.transaction_date.strftime('%Y-%m-%d')))
        pdf.text('Miti', text_padding, 5, align='L')
        pdf.text(': %s' % bs_date, value_width, 5, align='L')
        pdf.move_with(6)
        pdf.text('Invoice No.', text_padding, 5, align='L')
        pdf.text(': %s' % sale_voucher.voucher_no, value_width, 5, align='L')
        pdf.move_with(7)
        pdf.text('To,', text_padding, 5, align='L')
        pdf.move_with(7)
        pdf.tab(3)
        pdf.text(sale_voucher.get_billed_to(), horizontal_width, 5, align='L')
        pdf.move_with(6)
        pdf.tab(3)
        pdf.text(sale_voucher.address or '', horizontal_width, 5, align='L')
        pdf.move_with(6)
        pdf.tab(3)
        if sale_voucher.party and sale_voucher.party.tax_registration_number:
            pdf.text('VAT Reg No.: %s' % sale_voucher.party.tax_registration_number, horizontal_width - 70, 5,
                     align='L')
        pdf.text('Mode of Payment: : %s' % sale_voucher.mode, 70, 5, align='L')

        output = pdf.output()
        response = HttpResponse(output, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment;filename="somefilename.pdf"'
        return response


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


class ChequeVoucherViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = ChequeVoucherSerializer


class BankBranchViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    queryset = BankBranch.objects.all()
    serializer_class = BankBranchSerializer


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


class BankAccountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
