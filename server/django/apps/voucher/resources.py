from import_export import resources

from awecount.utils.resources import PrettyNameModelResource
from .models import SalesVoucher, SalesVoucherRow

INVOICE_EXCLUDES = ('party', 'discount_obj', 'bank_account', 'company', 'fiscal_year')


class InvoiceResource(PrettyNameModelResource):
    id = resources.Field('id', column_name='ID')
    voucher_no = resources.Field('voucher_no', column_name='Bill No.')
    party_name = resources.Field('party__name', column_name='Party')

    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class SalesVoucherResource(PrettyNameModelResource):
    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class SalesVoucherRowResource(PrettyNameModelResource):
    class Meta:
        model = SalesVoucherRow
