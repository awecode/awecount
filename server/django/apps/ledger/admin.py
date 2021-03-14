from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.ledger.models import Party, Category, JournalEntry, Transaction, Account, PartyRepresentative, \
    TransactionCharge, AccountOpeningBalance


class PartyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company__name')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number', 'company')
    list_filter = ('company',)


admin.site.register(Party, PartyAdmin)


class PartyRepresentativeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'phone', 'email', 'position')
    list_display = ('__str__', 'phone', 'email', 'position')
    list_display_links = ('__str__', 'phone', 'email', 'position')


admin.site.register(PartyRepresentative, PartyRepresentativeAdmin)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'parent', 'default')
    search_fields = ('company__name', 'code', 'name')
    list_filter = ('company', 'default')
    readonly_fields = ('default',)


class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('account__company', 'journal_entry__content_type')
    search_fields = ('journal_entry__date', 'journal_entry__object_id')


class TransactionInline(admin.TabularInline):
    model = Transaction


class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'content_type', 'object_id')
    inlines = [TransactionInline]


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'code', 'parent', 'company')
    list_filter = ('company', 'default')
    readonly_fields = ('default',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)


class TransactionChargeAdmin(admin.ModelAdmin):
    list_filter = ('company',)


admin.site.register(TransactionCharge, TransactionChargeAdmin)


class AccountOpeningBalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'opening_dr', 'opening_cr')
    search_fields = ('account__name', 'opening_dr', 'opening_cr')
    list_filter = ('company', 'fiscal_year')


admin.site.register(AccountOpeningBalance, AccountOpeningBalanceAdmin)
