from django.contrib import admin

from apps.voucher.models import SalesVoucher, SalesVoucherRow, CreditVoucher, CreditVoucherRow, Bank, BankBranch, \
    ChequeVoucher, InvoiceDesign, BankAccount, JournalVoucher, JournalVoucherRow


class SaleVoucherRowTabular(admin.TabularInline):
    model = SalesVoucherRow


class CreditVoucherRowTabular(admin.TabularInline):
    model = CreditVoucherRow


class JournalVoucherRowTabular(admin.TabularInline):
    model = JournalVoucherRow


class SalesVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'customer_name', 'address', 'user__full_name',
        'user__email', 'company__name', 'company__tax_registration_number', 'remarks', 'total_amount')
    list_filter = ('company', 'status', 'mode')
    list_display = ('company', 'voucher_no', 'party', 'customer_name', 'total_amount')
    inlines = (SaleVoucherRowTabular,)


class CreditVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'company__name',
        'company__tax_registration_number',)
    list_filter = ('company', 'party',)
    list_display = ('company', 'voucher_no', 'party', 'amount',)
    inlines = (CreditVoucherRowTabular,)


admin.site.register(SalesVoucher, SalesVoucherAdmin)
admin.site.register(SalesVoucherRow)
admin.site.register(CreditVoucher, CreditVoucherAdmin)
admin.site.register(CreditVoucherRow)
admin.site.register(Bank)
admin.site.register(BankBranch)
admin.site.register(ChequeVoucher)
admin.site.register(InvoiceDesign)
admin.site.register(BankAccount)


class JournalVoucherAdmin(admin.ModelAdmin):
    search_fields = ('voucher_no', 'date',)
    list_filter = ('company', 'status',)
    list_display = ('company', 'voucher_no', 'status', 'date',)
    inlines = (JournalVoucherRowTabular,)


admin.site.register(JournalVoucher, JournalVoucherAdmin)
