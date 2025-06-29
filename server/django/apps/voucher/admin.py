from django.contrib import admin
from django.urls import reverse

from apps.voucher.models import (
    Challan,
    ChallanRow,
    CreditNote,
    CreditNoteRow,
    DebitNote,
    DebitNoteRow,
    Import,
    PaymentReceipt,
    PurchaseDiscount,
    PurchaseVoucher,
    PurchaseVoucherRow,
    RecurringVoucherTemplate,
    SalesAgent,
    SalesDiscount,
    SalesVoucher,
    SalesVoucherRow,
    LandedCostRow,
)
from apps.voucher.models.invoice_design import InvoiceDesign
from apps.voucher.models.journal_vouchers import JournalVoucher, JournalVoucherRow
from apps.voucher.models.voucher_settings import PurchaseSetting, SalesSetting


class SaleVoucherRowTabular(admin.TabularInline):
    model = SalesVoucherRow
    autocomplete_fields = ["item", "tax_scheme", "discount_obj", "unit"]


class PurchaseVoucherRowTabular(admin.TabularInline):
    model = PurchaseVoucherRow


class CreditNoteRowTabular(admin.TabularInline):
    model = CreditNoteRow


class DebitNoteRowTabular(admin.TabularInline):
    model = DebitNoteRow


class JournalVoucherRowTabular(admin.TabularInline):
    model = JournalVoucherRow


class ChallanRowTabular(admin.TabularInline):
    model = ChallanRow


class SalesVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "party__name",
        "party__tax_identification_number",
        "customer_name",
        "address",
        "user__full_name",
        "user__email",
        "company__name",
        "company__tax_identification_number",
        "remarks",
    )
    list_filter = ("company", "status", "mode", "fiscal_year")
    list_display = (
        "company",
        "voucher_no",
        "party",
        "customer_name",
        "status",
        "total_amount",
    )
    inlines = (SaleVoucherRowTabular,)
    autocomplete_fields = [
        "party",
        "company",
        "discount_obj",
        "sales_agent",
        "bank_account",
        "challans",
        "user",
    ]

    def get_queryset(self, request, *args, **kwargs):
        qs = super(SalesVoucherAdmin, self).get_queryset(request)
        changelist_path = reverse(
            "admin:%s_%s_changelist"
            % (self.model._meta.app_label, self.model._meta.model_name)
        )
        if request.path == changelist_path:
            qs = qs.select_related(
                "party",
                "company",
            )
        return qs


class ImportAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "user",
        "type",
        "status",
        "created_at",
    )
    search_fields = ("company__name", "user__full_name")
    list_filter = ("company", "status", "type")


class CreditNoteAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "party__name",
        "party__tax_identification_number",
        "company__name",
        "company__tax_identification_number",
    )
    list_filter = (
        "company",
        "party",
    )
    list_display = ("company", "voucher_no", "party", "total_amount")
    inlines = (CreditNoteRowTabular,)


admin.site.register(SalesVoucher, SalesVoucherAdmin)
admin.site.register(SalesVoucherRow)
admin.site.register(CreditNote, CreditNoteAdmin)
admin.site.register(CreditNoteRow)
admin.site.register(InvoiceDesign)
admin.site.register(Import, ImportAdmin)


class DebitNoteAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "party__name",
        "party__tax_identification_number",
        "company__name",
        "company__tax_identification_number",
    )
    list_filter = (
        "company",
        "party",
    )
    list_display = ("company", "voucher_no", "party", "total_amount")
    inlines = (DebitNoteRowTabular,)


admin.site.register(DebitNote, DebitNoteAdmin)
admin.site.register(DebitNoteRow)


class JournalVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "date",
    )
    list_filter = (
        "company",
        "status",
    )
    list_display = (
        "company",
        "voucher_no",
        "status",
        "date",
    )
    inlines = (JournalVoucherRowTabular,)


admin.site.register(JournalVoucher, JournalVoucherAdmin)


class PurchaseVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "party__name",
        "party__tax_identification_number",
        "company__name",
        "company__tax_identification_number",
    )
    list_filter = ("company",)
    list_display = ("company", "voucher_no", "party", "total_amount")
    inlines = (PurchaseVoucherRowTabular,)


admin.site.register(PurchaseVoucher, PurchaseVoucherAdmin)


class DiscountAdmin(admin.ModelAdmin):
    search_fields = ("name", "value")
    list_filter = ("company", "type", "trade_discount")


admin.site.register(SalesDiscount, DiscountAdmin)
admin.site.register(PurchaseDiscount, DiscountAdmin)


class SalesAgentAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("company",)


admin.site.register(SalesAgent, SalesAgentAdmin)


class SalesSettingAdmin(admin.ModelAdmin):
    list_display = ("company",)
    search_fields = ("company__name",)
    list_filter = (
        "show_party_by_default",
        "show_trade_discount_in_voucher",
        "mode",
        "enable_row_description",
    )


admin.site.register(SalesSetting, SalesSettingAdmin)


class PurchaseSettingAdmin(admin.ModelAdmin):
    list_display = ("company",)
    search_fields = ("company__name",)
    list_filter = ("show_trade_discount_in_voucher", "mode", "enable_row_description")


admin.site.register(PurchaseSetting, PurchaseSettingAdmin)


class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ("date", "mode")
    list_filter = ("company", "mode")


admin.site.register(PaymentReceipt, PaymentReceiptAdmin)


class ChallanAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "party__name",
        "party__tax_identification_number",
        "company__name",
        "company__tax_identification_number",
    )
    list_filter = ("company",)
    list_display = (
        "company",
        "voucher_no",
        "party",
    )
    inlines = (ChallanRowTabular,)


admin.site.register(Challan, ChallanAdmin)


class PurchaseVoucherRowAdmin(admin.ModelAdmin):
    raw_id_fields = ("item",)
    readonly_fields = ["id"]


admin.site.register(PurchaseVoucherRow, PurchaseVoucherRowAdmin)


class LandedCostRowAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "value",
        "is_percentage",
        "amount",
        "tax_amount",
        "total_amount",
    )
    autocomplete_fields = ("credit_account", "tax_scheme", "invoice")


admin.site.register(LandedCostRow, LandedCostRowAdmin)


class RecurringVoucherTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "type",
        "is_active",
        "next_date",
        "no_of_vouchers_created",
    )
    search_fields = (
        "title",
        "company__name",
        "company__tax_identification_number",
    )
    list_filter = ("company", "type", "is_active")

admin.site.register(RecurringVoucherTemplate, RecurringVoucherTemplateAdmin)