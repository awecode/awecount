from django.contrib import admin

from .models import TaxScheme, TaxPayment


class TaxSchemeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name', 'description', 'company__name', 'rate')
    list_filter = ('recoverable', 'company', 'default')
    list_display = ('name', 'short_name', 'rate')


admin.site.register(TaxScheme, TaxSchemeAdmin)


class TaxPaymentAdmin(admin.ModelAdmin):
    search_fields = ('tax_scheme__name', 'tax_scheme__short_name', 'company__name', 'voucher_no', 'amount', 'remarks')
    list_filter = ('company', 'cr_account', 'status')
    list_display = ('date', 'voucher_no', 'amount')


admin.site.register(TaxPayment, TaxPaymentAdmin)