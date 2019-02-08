from django.contrib import admin

from apps.voucher.models import SalesVoucher


class SalesVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        'voucher_no', 'party__name', 'party__tax_registration_number', 'customer_name', 'address', 'user__full_name',
        'user__email', 'company__name', 'company__tax_registration_number', 'remarks', 'total_amount')
    list_filter = ('company', 'status', 'mode')
    list_display = ('company', 'voucher_no', 'party', 'customer_name', 'total_amount')


admin.site.register(SalesVoucher, SalesVoucherAdmin)
