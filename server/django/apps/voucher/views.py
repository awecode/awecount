import os
import uuid

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django_xhtml2pdf.utils import fetch_resources
from django_xhtml2pdf.views import PdfMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

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
            filename = f"{uuid.uuid4()}-{file.name}"
            if folder:
                filename = f"{folder}/{filename}"
                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, folder))
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            file_urls.append(filename)

        return Response(file_urls)
