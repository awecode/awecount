from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from mptt.admin import MPTTModelAdmin

from apps.ledger.models import Party, Category, JournalEntry, Transaction, Account, PartyRepresentative, \
    TransactionCharge, AccountOpeningBalance, AccountClosing


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
    list_filter = ('company', 'default', 'category')
    readonly_fields = ('default',)


class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('account__company', 'journal_entry__content_type')
    search_fields = ('journal_entry__date', 'journal_entry__object_id')
    raw_id_fields = ('account', 'journal_entry')


class TransactionInline(admin.TabularInline):
    model = Transaction
    raw_id_fields = ('account', 'journal_entry')


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


def run_account_closing(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, 'Please select exactly one account closing instance.')
        return
    instance: AccountClosing = queryset.first()
    company = instance.company
    date = instance.fiscal_period.end

    income_category = Category.objects.get(name='Income', company=company, default=True, parent__isnull=True)
    income_accounts = Account.objects.filter(category__in=income_category.get_descendants(include_self=True))

    expenses_category = Category.objects.get(name='Expenses', company=company, default=True, parent__isnull=True)
    expenses_accounts = Account.objects.filter(category__in=expenses_category.get_descendants(include_self=True))

    journal_entry = JournalEntry.objects.create(date=date, content_type=ContentType.objects.get_for_model(instance),
                                                object_id=instance.id, type='Closing')
    jeid = journal_entry.id

    transactions = []

    for income_account in income_accounts:
        amount = income_account.get_day_closing(until_date=date)
        transaction = Transaction(account=income_account, dr_amount=amount, type='Closing', journal_entry_id=jeid)
        transactions.append(transaction)

    for expense_account in expenses_accounts:
        amount = expense_account.get_day_closing(until_date=date)
        transaction = Transaction(account=expense_account, cr_amount=amount, type='Closing', journal_entry_id=jeid)
        transactions.append(transaction)


@admin.register(AccountClosing)
class AccountClosingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
    list_filter = ('status',)
    search_fields = ('company__name', 'fiscal_year')
    actions = (run_account_closing,)
