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
    # readonly_fields = ('default',)


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
    if instance.status == 'Closed':
        messages.warning(request, 'Already closed.')
        return
    company = instance.company
    date = instance.fiscal_period.end

    pl_account = Account.objects.get(name='Profit and Loss Account', default=True, company=company)

    income_category = Category.objects.get(name='Income', company=company, default=True, parent__isnull=True)
    income_accounts = Account.objects.filter(category__in=income_category.get_descendants(include_self=True))

    expenses_category = Category.objects.get(name='Expenses', company=company, default=True, parent__isnull=True)
    expenses_accounts = Account.objects.filter(category__in=expenses_category.get_descendants(include_self=True))

    journal_entry = JournalEntry.objects.create(date=date, content_type=ContentType.objects.get_for_model(instance),
                                                object_id=instance.id, type='Closing')
    jeid = journal_entry.id

    transactions = []

    total_income_amount = 0
    for income_account in income_accounts:
        income_amount = income_account.get_day_closing(until_date=date)
        # Amount is usually negative for Income
        income_amount = -1 * income_amount
        total_income_amount += income_amount
        # TODO What if amount is positive?
        if income_amount:
            transaction = Transaction(account=income_account, dr_amount=income_amount, type='Closing',
                                      journal_entry_id=jeid,
                                      company_id=company.id)
            transactions.append(transaction)

    total_expense_amount = 0
    for expense_account in expenses_accounts:
        expense_amount = expense_account.get_day_closing(until_date=date)
        # Amount is usually positive for Expense
        # TODO What if amount is negative?
        total_expense_amount += expense_amount

        if expense_amount:
            transaction = Transaction(account=expense_account, cr_amount=expense_amount, type='Closing',
                                      journal_entry_id=jeid,
                                      company_id=company.id)
            transactions.append(transaction)

    diff = total_income_amount - total_expense_amount

    if diff > 0:
        pl_transaction = Transaction(account=pl_account, journal_entry_id=jeid, company_id=company.id, cr_amount=diff,
                                     type='Closing')
    else:
        pl_transaction = Transaction(account=pl_account, journal_entry_id=jeid, company_id=company.id,
                                     dr_amount=-1 * diff,
                                     type='Closing')

    transactions.append(pl_transaction)

    Transaction.objects.bulk_create(transactions)
    instance.journal_entry = journal_entry
    instance.status = 'Closed'
    instance.save()
    messages.success(request, 'Closed all income and expense accounts.')


def undo_account_closing(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, 'Please select exactly one account closing instance.')
        return
    instance: AccountClosing = queryset.first()
    if instance.status != 'Closed':
        messages.warning(request, 'This is not closed.')
        return

    journal_entry = instance.journal_entry
    instance.journal_entry = None
    instance.status = 'Pending'
    instance.save()
    journal_entry.delete()
    messages.success(request, 'Reverted account closing.')


@admin.register(AccountClosing)
class AccountClosingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
    list_filter = ('status', 'company')
    search_fields = ('company__name', 'fiscal_year')
    actions = (run_account_closing, undo_account_closing)
    readonly_fields = ('status', 'journal_entry',)
    ordering = ('-fiscal_period__start',)
