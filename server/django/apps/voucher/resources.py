from import_export import resources
from import_export.fields import Field

from awecounting.libs.resources import PrettyNameModelResource

from .models import (
    CreditNote,
    CreditNoteRow,
    DebitNote,
    DebitNoteRow,
    PurchaseVoucher,
    PurchaseVoucherRow,
    SalesVoucher,
    SalesVoucherRow,
)

INVOICE_EXCLUDES = ("party", "discount_obj", "bank_account", "company", "fiscal_year")
INVOICEROW_EXCLUDES = ("item", "unit", "tax_scheme")


class InvoiceResource(PrettyNameModelResource):
    id = resources.Field("id", column_name="ID")
    voucher_no = resources.Field("voucher_no", column_name="Bill No.")
    fiscal_year = resources.Field("fiscal_year__name", column_name="Fiscal Year")
    party_name = resources.Field("party__name", column_name="Party")

    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class InvoiceRowResource(PrettyNameModelResource):
    id = resources.Field("id", column_name="ID")
    voucher_id = resources.Field("voucher_id", column_name="Voucher ID")
    item_name = resources.Field("item__name", column_name="Item")
    unit_name = resources.Field("unit__name", column_name="Unit")
    tax_name = resources.Field("tax_scheme__name", column_name="Tax")
    tax_rate = resources.Field("tax_scheme__rate", column_name="Tax Rate")

    class Meta:
        exclude = INVOICEROW_EXCLUDES


class SalesVoucherResource(InvoiceResource):
    class Meta:
        model = SalesVoucher


class SalesVoucherRowResource(InvoiceRowResource):
    class Meta:
        model = SalesVoucherRow


class BooleanWidget(resources.widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        pass


class PurchaseVoucherResource(PrettyNameModelResource):
    user = Field(attribute="user__full_name", column_name="User")
    fiscal_year = Field(attribute="fiscal_year__name", column_name="Fiscal Year")
    company = Field(attribute="company__name", column_name="Company")
    discount_obj = Field(attribute="discount_obj__name", column_name="Discount Object")
    bank_account = Field(
        attribute="bank_account__account_name", column_name="Bank Account"
    )
    party = Field(attribute="party__name", column_name="Party")
    imported = Field(
        attribute="is_import", column_name="Import", widget=BooleanWidget()
    )

    class Meta:
        model = PurchaseVoucher
        fields = [
            "id",
            "voucher_no",
            "date",
            "due_date",
            "party",
            "status",
            "mode",
            "bank_account",
            "discount_type",
            "discount",
            "trade_discount",
            "discount_obj",
            "remarks",
            "imported",
            "total_amount",
            "company",
            "user",
            "fiscal_year",
        ]
        export_order = fields


class PurchaseVoucherRowResource(PrettyNameModelResource):
    voucher = Field(attribute="voucher__voucher_no", column_name="Voucher")
    item = Field(attribute="item__name", column_name="Item")
    unit = Field(attribute="unit__name", column_name="Unit")
    trade_discount = Field(
        attribute="trade_discount", column_name="Trade Discount", widget=BooleanWidget()
    )
    discount_obj = Field(attribute="discount_obj__name", column_name="Discount Object")
    tax_scheme = Field(attribute="tax_scheme__name", column_name="Tax Scheme")
    trade_discount = Field(
        attribute="trade_discount", column_name="Trade Discount", widget=BooleanWidget()
    )
    company = Field(attribute="company__name", column_name="Company")

    class Meta:
        model = PurchaseVoucherRow
        fields = [
            "id",
            "voucher",
            "item",
            "description",
            "quantity",
            "unit",
            "rate",
            "discount",
            "tax_amount",
            "discount_type",
            "trade_discount",
            "discount_obj",
            "tax_scheme",
            "discount_amount",
            "tax_amount",
            "net_amount",
            "company",
        ]
        export_order = fields


class CreditNoteResource(PrettyNameModelResource):
    class Meta:
        model = CreditNote


class CreditNoteRowResource(PrettyNameModelResource):
    class Meta:
        model = CreditNoteRow


class DebitNoteResource(PrettyNameModelResource):
    class Meta:
        model = DebitNote


class DebitNoteRowResource(PrettyNameModelResource):
    class Meta:
        model = DebitNoteRow
