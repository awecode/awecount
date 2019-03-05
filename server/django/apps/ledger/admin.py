from django.contrib import admin

from apps.ledger.models import Party, Category, JournalEntry, Transaction, Account


class PartyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company__name')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company')
    list_filter = ('company',)


admin.site.register(Party, PartyAdmin)

admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(JournalEntry)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company',)


admin.site.register(Category, CategoryAdmin)
