from django.contrib import admin

from apps.product.models import Brand
from apps.voucher.models import SalesVoucher, SalesVoucherRow, CreditNote, CreditNoteRow, InvoiceDesign, \
    JournalVoucher, JournalVoucherRow, PurchaseVoucher, PurchaseVoucherRow, SalesDiscount, PurchaseDiscount, DebitNoteRow, \
    DebitNote


class SaleVoucherRowTabular(admin.TabularInline):
    model = SalesVoucherRow


class PurchaseVoucherRowTabular(admin.TabularInline):
    model = PurchaseVoucherRow


class CreditNoteRowTabular(admin.TabularInline):
    model = CreditNoteRow


class DebitNoteRowTabular(admin.TabularInline):
    model = DebitNoteRow


class JournalVoucherRowTabular(admin.TabularInline):
    model = JournalVoucherRow


class SalesVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'customer_name', 'address', 'user__full_name',
        'user__email', 'company__name', 'company__tax_registration_number', 'remarks',)
    list_filter = ('company', 'status', 'mode', 'fiscal_year')
    list_display = ('company', 'voucher_no', 'party', 'customer_name', 'status',)
    inlines = (SaleVoucherRowTabular,)


class CreditNoteAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'company__name',
        'company__tax_registration_number',)
    list_filter = ('company', 'party',)
    list_display = ('company', 'voucher_no', 'party')
    inlines = (CreditNoteRowTabular,)


admin.site.register(SalesVoucher, SalesVoucherAdmin)
admin.site.register(SalesVoucherRow)
admin.site.register(CreditNote, CreditNoteAdmin)
admin.site.register(CreditNoteRow)
admin.site.register(InvoiceDesign)


class DebitNoteAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'company__name',
        'company__tax_registration_number',)
    list_filter = ('company', 'party',)
    list_display = ('company', 'voucher_no', 'party')
    inlines = (DebitNoteRowTabular,)


admin.site.register(DebitNote, DebitNoteAdmin)
admin.site.register(DebitNoteRow)


class JournalVoucherAdmin(admin.ModelAdmin):
    search_fields = ('voucher_no', 'date',)
    list_filter = ('company', 'status',)
    list_display = ('company', 'voucher_no', 'status', 'date',)
    inlines = (JournalVoucherRowTabular,)


admin.site.register(JournalVoucher, JournalVoucherAdmin)


class PurchaseVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'company__name',
        'company__tax_registration_number')
    list_filter = ('company',)
    list_display = ('company', 'voucher_no', 'party',)
    inlines = (PurchaseVoucherRowTabular,)


admin.site.register(PurchaseVoucher, PurchaseVoucherAdmin)


class DiscountAdmin(admin.ModelAdmin):
    search_fields = ('name', 'value')
    list_filter = ('company', 'type', 'trade_discount')


admin.site.register(SalesDiscount, DiscountAdmin)
admin.site.register(PurchaseDiscount, DiscountAdmin)


class BrandAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_filter = ('company',)


admin.site.register(Brand, BrandAdmin)
