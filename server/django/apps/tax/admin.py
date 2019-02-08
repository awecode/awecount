from django.contrib import admin

from apps.tax.models import TaxScheme


class TaxSchemeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name', 'description', 'company__name', 'rate')
    list_filter = ('recoverable', 'company', 'default')
    list_display = ('name', 'short_name', 'rate')


admin.site.register(TaxScheme, TaxSchemeAdmin)
