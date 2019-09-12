from import_export import resources

from awecount.utils.resources import PrettyNameModelResource
from .models import SalesVoucher, SalesVoucherRow, PurchaseVoucher, PurchaseVoucherRow

INVOICE_EXCLUDES = ('party', 'discount_obj', 'bank_account', 'company', 'fiscal_year')
INVOICEROW_EXCLUDES = ('item', 'unit', 'tax_scheme')


class InvoiceResource(PrettyNameModelResource):
    id = resources.Field('id', column_name='ID')
    voucher_no = resources.Field('voucher_no', column_name='Bill No.')
    fiscal_year = resources.Field('fiscal_year__name', column_name='Fiscal Year')
    party_name = resources.Field('party__name', column_name='Party')

    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class InvoiceRowResource(PrettyNameModelResource):
    id = resources.Field('id', column_name='ID')
    voucher_id = resources.Field('voucher_id', column_name='Voucher ID')
    item_name = resources.Field('item__name', column_name='Item')
    unit_name = resources.Field('unit__name', column_name='Unit')
    tax_name = resources.Field('tax_scheme__name', column_name='Tax')
    tax_rate = resources.Field('tax_scheme__rate', column_name='Tax Rate')

    class Meta:
        exclude = INVOICEROW_EXCLUDES


class SalesVoucherResource(InvoiceResource):
    class Meta:
        model = SalesVoucher


class SalesVoucherRowResource(InvoiceRowResource):
    class Meta:
        model = SalesVoucherRow


class PurchaseVoucherResource(PrettyNameModelResource):
    class Meta:
        model = PurchaseVoucher


class PurchaseVoucherRowResource(PrettyNameModelResource):
    class Meta:
        model = PurchaseVoucherRow
