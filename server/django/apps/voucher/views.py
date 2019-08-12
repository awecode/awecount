from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from io import BytesIO

from django.views.generic.detail import DetailView
from django_xhtml2pdf.utils import PdfResponse, fetch_resources
from django_xhtml2pdf.views import PdfMixin
from xhtml2pdf import pisa

from .models import SalesVoucher


class SalesVoucherPdfView(PdfMixin, DetailView):
    model = SalesVoucher
    template_name = "sale_voucher_pdf.html"

    def render(self):
        retval = super(PdfResponse, self).render()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisa.CreatePDF(
            self.rendered_content,
            dest=response,
            link_callback=fetch_resources)
        return response
