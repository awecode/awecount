from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.ledger.models import Party, Category, JournalEntry, Transaction, Account, PartyRepresentative, TransactionCharge


class PartyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company__name')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company')
    list_filter = ('company',)


admin.site.register(Party, PartyAdmin)
admin.site.register(PartyRepresentative)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'current_dr', 'current_cr', 'category', 'parent', 'default')
    search_fields = ('company__name', 'code', 'name')
    list_filter = ('company', 'default')
    readonly_fields = ('default',)


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction)
admin.site.register(JournalEntry)


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'code', 'parent', 'company')
    list_filter = ('company', 'default')
    readonly_fields = ('default',)


admin.site.register(Category, CategoryAdmin)


class TransactionChargeAdmin(admin.ModelAdmin):
    list_filter = ('company',)


admin.site.register(TransactionCharge, TransactionChargeAdmin)
