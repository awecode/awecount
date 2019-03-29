from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework.decorators import action
from rest_framework.response import Response
from xhtml2pdf import pisa

from awecount.utils import get_next_voucher_no, link_callback
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import DeleteRows, InputChoiceMixin
from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES, STATUSES, MODES, CreditVoucher, CreditVoucherRow, \
    BankBranch, InvoiceDesign, BankAccount
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditVoucherCreateSerializer, \
    CreditVoucherListSerializer, ChequeVoucherSerializer, BankBranchSerializer, InvoiceDesignSerializer, \
    BankAccountSerializer, SaleVoucherRowCreditNoteOptionsSerializer


# class GenerateInvoice:
#     def __init__(self, startY, default_font_size):
#         self.pdf = FPDF('P', 'mm', 'A4')
#         self.pdf.add_page()
#         self.pdf.set_margins(20, 10, 20)
#         self.currentY = startY
#         self.pdf.set_y(startY)
#         self.default_font_size = default_font_size
#         self.pdf.set_font('Arial', '', default_font_size)
#
#     def move_with(self, value):
#         self.currentY += value
#         self.pdf.set_y(self.currentY)
#
#     def tab(self, padding):
#         self.pdf.cell(padding)
#
#     def textWidth(self, text, height=50, font_size=12, font_type='', align='L'):
#         width = self.pdf.get_string_width(text)
#         width += 5
#         self.btext(text, width, height, font_size, font_type, align)
#
#     def btext(self, text, width=200, height=50, font_size=12, font_type='', align='L'):
#         self.pdf.set_font('Arial', font_type, font_size)
#         self.pdf.cell(width, height, text, 1, 0, align)
#
#     def text(self, text, width=200, height=50, font_size=12, font_type='', align='L'):
#         self.pdf.set_font('Arial', font_type, font_size)
#         self.pdf.cell(width, height, text, 0, 0, align)
#
#     def draw_line(self):
#         self.pdf.line(20, 45, 190, 45)
#
#     def output(self):
#         return self.pdf.output(dest='S').encode('latin-1')


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

    @action(detail=True)
    def rows(self, request, pk):
        sale_voucher = self.get_object()
        sale_voucher_rows = sale_voucher.rows.all()
        data = SaleVoucherRowCreditNoteOptionsSerializer(sale_voucher_rows, many=True).data
        return Response(data)


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
