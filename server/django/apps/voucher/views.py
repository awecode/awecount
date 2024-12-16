from django.conf import settings
from django.forms import ValidationError
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django_xhtml2pdf.utils import fetch_resources
from django_xhtml2pdf.views import PdfMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

from apps.company.models import Company
from awecount.libs.helpers import upload_file

from .models import SalesVoucher


class SalesVoucherPdfView(PdfMixin, DetailView):
    model = SalesVoucher
    template_name = "sale_voucher_pdf.html"

    def render(self):
        # retval = super(PdfResponse, self).render()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="report.pdf"'
        pisa.CreatePDF(
            self.rendered_content, dest=response, link_callback=fetch_resources
        )
        return response


class FileUploadView(APIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        uploaded_files = request.FILES.getlist("files")
        folder = request.data.get("folder", "")
        file_urls = []

        for file in uploaded_files:
            max_file_upload_size = settings.MAX_FILE_UPLOAD_SIZE
            if file.size > max_file_upload_size:
                max_file_upload_size_mb = max_file_upload_size / (1024 * 1024)
                raise ValidationError(
                    f"File size exceeds the maximum limit of {max_file_upload_size_mb:.2f} MB"
                )

        for file in uploaded_files:
            filename = upload_file(file, folder)
            file_urls.append(filename)

        return Response(file_urls)


class InvoiceSettingUpdateView(APIView):
    model = Company
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        invoice_template = request.data.get("invoice_template")
        if invoice_template not in dict(Company.TEMPLATE_CHOICES):
            return Response({"message": "Invalid invoice template"}, status=400)
        company = Company.objects.get(pk=request.company_id)
        company.invoice_template = invoice_template
        company.save()
        return Response({})
