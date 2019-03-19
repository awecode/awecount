import json
import cv2
import re
from django.http import HttpResponse
from matplotlib import pyplot as plt
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from .models import SalesVoucher, SalesVoucherRow, DISCOUNT_TYPES, STATUSES, MODES, CreditVoucher, CreditVoucherRow, \
    ChequeVoucher, BankBranch, InvoiceDesign, BankAccount
from .serializers import SalesVoucherCreateSerializer, SalesVoucherListSerializer, CreditVoucherCreateSerializer, \
    CreditVoucherListSerializer, ChequeVoucherSerializer, BankBranchSerializer, InvoiceDesignSerializer, \
    BankAccountSerializer
from awecount.utils import get_next_voucher_no
from awecount.utils.mixins import DeleteRows, InputChoiceMixin


class GenerateInvoice:
    def __init__(self, image_path, canvas):
        self.image = cv2.imread(image_path)
        self.canvas = json.loads(canvas)
        self.padding = 0
        self.attributes = {}
        self.parse_attributes()

    def to_snake_case(self, string):
        text = re.sub(r'[\s-]', '_', str(string))
        return text.lower()

    def parse_attributes(self):
        for data in self.objects():
            key = self.to_snake_case(data.get('text'))
            self.attributes[key] = dict(
                x=data.get('left'),
                y=data.get('top'),
                width=data.get('width'),
                height=data.get('height'),
                scale=data.get('scale'),
                font_size=data.get('fontSize'),
            )

    def objects(self):
        return self.canvas.get('objects')

    def __len__(self):
        return len(self.objects())

    def show(self):
        plt.imshow(self.image, cmap='grey')
        plt.show()


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

    @action(detail=False)
    def pdf(self, request):
        company = request.company
        invoice_template = company.invoice
        design = invoice_template.design
        file = design.file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment;filename="somefilename.pdf"'
        p = canvas.Canvas(response)
        p.drawString(0, 0, "Hello world.")
        p.showPage()
        p.save()
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
