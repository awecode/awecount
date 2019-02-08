from django.contrib import admin

from apps.ledger.models import Party


class PartyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')


admin.site.register(Party, PartyAdmin)
