from datetime import datetime, timedelta

from decimal import ROUND_HALF_UP, localcontext
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.users.models import Company
from apps.users.signals import company_creation
from awecount.utils import zero_for_none, none_for_zero, decimalize


class Category(MPTTModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    code = models.CharField(max_length=20, null=True, blank=True)
    default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ledger_categories')

    def __str__(self):
        return self.name

    def get_data(self):
        node = Node(self)
        return node.get_data()

    def get_descendant_accounts(self):
        ledgers = self.accounts.all()
        for descendant in self.get_descendants():
            ledgers = ledgers | descendant.accounts.all()
        return ledgers

    class Meta:
        verbose_name_plural = u'Categories'


class Account(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    current_dr = models.FloatField(null=True, blank=True)
    current_cr = models.FloatField(null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, related_name='accounts', blank=True, null=True, on_delete=models.SET_NULL)
    tax_rate = models.FloatField(blank=True, null=True)
    opening_dr = models.FloatField(default=0)
    opening_cr = models.FloatField(default=0)
    # fy = models.ForeignKey(FiscalYear, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ledger_accounts')

    def get_absolute_url(self):
        # return '/ledger/' + str(self.id)
        return 'url'

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_UP
            val = zero_for_none(self.current_dr) - zero_for_none(self.current_cr)
            return float(round(decimalize(val), 2))

    def get_day_opening_dr(self, before_date=None):
        if not before_date:
            before_date = datetime.date.today()
        transactions = Transaction.objects.filter(account=self, journal_entry__date__lt=before_date).order_by(
            '-journal_entry__id', '-journal_entry__date')[:1]
        if len(transactions) > 0:
            return transactions[0].current_dr
        return self.current_dr

    def get_day_opening_cr(self, before_date=None):
        if not before_date:
            before_date = datetime.date.today()
        transactions = Transaction.objects.filter(account=self, journal_entry__date__lt=before_date).order_by(
            '-journal_entry__id', '-journal_entry__date')[:1]
        if len(transactions) > 0:
            return transactions[0].current_cr
        return self.current_cr

    def get_day_opening(self, before_date=None):
        if not before_date:
            before_date = datetime.date.today()
        transactions = Transaction.objects.filter(account=self, journal_entry__date__lt=before_date).order_by(
            '-journal_entry__id', '-journal_entry__date')[:1]
        if len(transactions) > 0:
            return zero_for_none(transactions[0].current_dr) - zero_for_none(transactions[0].current_cr)
        return self.opening_dr - self.opening_cr

    def add_category(self, category):
        category_instance = Category.objects.get(name=category, company=self.company, default=True)
        self.category = category_instance

    def get_all_categories(self):
        return self.category.get_ancestors(include_self=True)

    categories = property(get_all_categories)

    def get_cr_amount(self, day):
        transactions = Transaction.objects.filter(journal_entry__date__lt=day, account=self).order_by(
            '-journal_entry__id', '-journal_entry__date')[:1]
        if len(transactions) > 0:
            return transactions[0].current_cr
        return 0

    def get_dr_amount(self, day):
        transactions = Transaction.objects.filter(journal_entry__date__lt=day, account=self).order_by(
            '-journal_entry__id', '-journal_entry__date')[:1]
        if len(transactions) > 0:
            return transactions[0].current_dr
        return 0

    # def save(self, *args, **kwargs):
    #     super().save()

    # def save(self, *args, **kwargs):
    #     queryset = Account.objects.all()
    #     original_name = self.name
    #     nxt = 2
    #     if not self.pk:
    #         while queryset.filter(**{'name': self.name, 'fy': self.fy}):
    #             self.name = original_name
    #             end = '%s%s' % ('-', nxt)
    #             if len(self.name) + len(end) > 100:
    #                 self.name = self.name[:100 - len(end)]
    #             self.name = '%s%s' % (self.name, end)
    #             nxt += 1
    #     return super(Account, self).save(*args, **kwargs)

    def suggest_code(self):
        if self.category:
            cat_code = self.category.code or ''
            max = 0
            for account in self.category.accounts.all():
                code = account.code.strip(cat_code + '-')
                if code.isdigit() and int(code) > max:
                    max = int(code)
            if cat_code:
                self.code = cat_code + '-' + str(max + 1)
            else:
                self.code = str(max + 1)

    def __str__(self):
        return self.name

    class Meta:
        # unique_together = ('name', 'fy')
        ordering = ('order',)


class Party(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tax_registration_number = models.IntegerField(blank=True, null=True)
    supplier_account = models.OneToOneField(Account, null=True, related_name='supplier_detail',
                                            on_delete=models.SET_NULL)
    customer_account = models.OneToOneField(Account, null=True, related_name='customer_detail',
                                            on_delete=models.SET_NULL)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='parties')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Parties'

    def save(self, *args, **kwargs):
        post_save = False
        if self.pk is None:
            post_save = True
        super().save(*args, **kwargs)
        if post_save:
            if not self.customer_account:
                customer_account = Account(name=self.name, company=self.company, code='PR-' + str(self.id))
                customer_account.name += ' (Receivable)'
                try:
                    customer_account.category = Category.objects.get(name='Customers',
                                                                     parent__name='Account Receivables',
                                                                     company=self.company)
                except Category.DoesNotExist:
                    pass
                customer_account.save()
                self.customer_account = customer_account
            if not self.supplier_account:
                try:
                    account2 = Account(name=self.name + ' (Payable)', code='PR-' + str(self.id))
                    account2.company = self.company
                    account2.category = Category.objects.get(name='Suppliers', parent__name='Account Payables',
                                                             company=self.company)
                    account2.save()
                    self.supplier_account = account2
                except Category.DoesNotExist:
                    pass
            self.save()


class PartyRepresentative(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='representative')

    company_id_accessor = 'party__company_id'


class Node(object):
    def __init__(self, model, parent=None, depth=0):
        self.children = []
        self.model = model
        self.name = self.model.name
        self.type = self.model.__class__.__name__
        self.dr = 0
        self.cr = 0
        self.url = None
        self.depth = depth
        self.parent = parent
        if self.type == 'Category':
            for child in self.model.children.all():
                self.add_child(Node(child, parent=self, depth=self.depth + 1))
            for account in self.model.accounts.all():
                self.add_child(Node(account, parent=self, depth=self.depth + 1))
        if self.type == 'Account':
            self.dr = self.model.current, 'company_dr or 0'
            self.cr = self.model.current_cr or 0
            self.url = self.model.get_absolute_url()
        if self.parent:
            self.parent.dr += self.dr
            self.parent.cr += self.cr

    def add_child(self, obj):
        self.children.append(obj.get_data())

    def get_data(self):
        data = {
            'name': self.name,
            'type': self.type,
            'dr': self.dr,
            'cr': self.cr,
            'nodes': self.children,
            'depth': self.depth,
            'url': self.url,
        }
        return data

    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    date = models.DateField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='journal_entries')
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.content_type) + ': ' + str(self.object_id) + ' [' + str(self.date) + ']'

    @staticmethod
    def get_for(source):
        try:
            return JournalEntry.objects.get(content_type=ContentType.objects.get_for_model(source), object_id=source.id)
        except JournalEntry.DoesNotExist:
            return None

    class Meta:
        verbose_name_plural = u'Journal Entries'


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    dr_amount = models.FloatField(null=True, blank=True)
    cr_amount = models.FloatField(null=True, blank=True)
    current_dr = models.FloatField(null=True, blank=True)
    current_cr = models.FloatField(null=True, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, related_name='transactions', on_delete=models.CASCADE)

    def get_balance(self):
        return zero_for_none(self.current_dr) - zero_for_none(self.current_cr)

    def __str__(self):
        return str(self.account) + ' [' + str(self.dr_amount) + ' / ' + str(self.cr_amount) + ']'


def alter(account, date, dr_difference, cr_difference):
    Transaction.objects.filter(journal_entry__date__gt=date, account=account).update(
        current_dr=none_for_zero(zero_for_none(F('current_dr')) + zero_for_none(dr_difference)),
        current_cr=none_for_zero(zero_for_none(F('current_cr')) + zero_for_none(cr_difference)))


def set_transactions(submodel, date, *entries, check=True, clear=False):
    """

    :param date: datetime object
    :param submodel: source model
    :param check: boolean - checks for debit/credit mismatch
    :type clear: object
    Clears all transactions not accounted here
    """
    # print(args)
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    journal_entry, created = JournalEntry.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(submodel), object_id=submodel.id,
        defaults={
            'date': date
        })
    dr_total = 0
    cr_total = 0
    all_accounts = []
    all_transaction_ids = []
    for arg in entries:
        # transaction = Transaction(account=arg[1], dr_amount=arg[2])
        matches = journal_entry.transactions.filter(account=arg[1])
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_UP
            val = round(decimalize(arg[2]), 2)
        all_accounts.append(arg[1])
        if not matches:
            transaction = Transaction()
            transaction.account = arg[1]
            if arg[0] == 'dr':
                transaction.dr_amount = val
                transaction.cr_amount = None
                transaction.account.current_dr = none_for_zero(
                    decimalize(transaction.account.current_dr) + decimalize(transaction.dr_amount))
                alter(arg[1], date, val, 0)
                dr_total += val
            if arg[0] == 'cr':
                transaction.cr_amount = val
                transaction.dr_amount = None
                transaction.account.current_cr = none_for_zero(
                    decimalize(transaction.account.current_cr) + decimalize(transaction.cr_amount))
                alter(arg[1], date, 0, val)
                cr_total += val

            transaction.current_dr = none_for_zero(
                round(decimalize(transaction.account.get_dr_amount(date + timedelta(days=1)))
                      + decimalize(transaction.dr_amount), 2)
            )
            transaction.current_cr = none_for_zero(
                round(decimalize(transaction.account.get_cr_amount(date + timedelta(days=1)))
                      + decimalize(transaction.cr_amount), 2)
            )
        else:
            transaction = matches[0]
            transaction.account = arg[1]

            # cancel out existing dr_amount and cr_amount from current_dr and current_cr
            # if transaction.dr_amount:
            #     transaction.current_dr -= transaction.dr_amount
            #     transaction.account.current_dr -= transaction.dr_amount
            #
            # if transaction.cr_amount:
            #     transaction.current_cr -= transaction.cr_amount
            #     transaction.account.current_cr -= transaction.cr_amount

            # save new dr_amount and add it to current_dr/cr

            if arg[0] == 'dr':
                dr_difference = val - decimalize(transaction.dr_amount)
                cr_difference = decimalize(transaction.cr_amount) * -1
                alter(arg[1], transaction.journal_entry.date, dr_difference, cr_difference)
                transaction.dr_amount = val
                transaction.cr_amount = None
                dr_total += transaction.dr_amount
            else:
                cr_difference = val - decimalize(transaction.cr_amount)
                dr_difference = decimalize(transaction.dr_amount) * -1
                alter(arg[1], transaction.journal_entry.date, dr_difference, cr_difference)
                transaction.cr_amount = val
                transaction.dr_amount = None
                cr_total += transaction.cr_amount

            transaction.current_dr = none_for_zero(decimalize(transaction.current_dr) + dr_difference)
            transaction.current_cr = none_for_zero(decimalize(transaction.current_cr) + cr_difference)
            transaction.account.current_dr = none_for_zero(
                decimalize(transaction.account.current_dr) + dr_difference)
            transaction.account.current_cr = none_for_zero(
                decimalize(transaction.account.current_cr) + cr_difference)

        # the following code lies outside if,else block, inside for loop
        transaction.account.save()
        # new transactions if any are saved into db by following code
        try:
            journal_entry.transactions.add(transaction, bulk=False)
        except TypeError:  # for Django <1.9
            journal_entry.transactions.add(transaction)
        all_transaction_ids.append(transaction.id)

    if clear:
        obsolete_transactions = journal_entry.transactions.exclude(id__in=all_transaction_ids)
        obsolete_transactions.delete()
    if check and round(dr_total, 2) != round(cr_total, 2):
        error_msg = 'Dr/Cr mismatch from {0}, ID: {1}, Dr: {2}, Cr: {3}'.format(str(submodel), submodel.id, dr_total, cr_total)
        # mail_admins('Dr/Cr mismatch!', error_msg)
        print(entries)
        raise RuntimeError(error_msg)


@receiver(pre_delete, sender=Transaction)
def _transaction_delete(sender, instance, **kwargs):
    transaction = instance
    if transaction.dr_amount:
        transaction.account.current_dr -= transaction.dr_amount

    if transaction.cr_amount:
        transaction.account.current_cr -= transaction.cr_amount

    alter(transaction.account, transaction.journal_entry.date, float(zero_for_none(transaction.dr_amount)) * -1,
          float(zero_for_none(transaction.cr_amount)) * -1)

    transaction.account.save()


def delete_rows(rows, model):
    for row in rows:
        if row.get('id'):
            instance = model.objects.get(id=row.get('id'))
            try:
                JournalEntry.objects.get(content_type=ContentType.objects.get_for_model(model),
                                         object_id=instance.id).delete()
            except:
                pass
            instance.delete()


@receiver(company_creation)
def handle_company_creation(sender, **kwargs):
    company = kwargs.get('company')
    # TODO make default Categories uneditable
    # TODO Prevent calling twice
    # CREATE DEFAULT CATEGORIES AND LEDGERS FOR EQUITY

    equity = Category.objects.create(name='Equity', code='E', company=company, default=True)
    # Account.objects.create(name='Paid in Capital', category=equity, code='E-PC', company=company, default=True)
    # Account.objects.create(name='Retained Earnings', category=equity, code='E-RE', company=company, default=True)
    # Account.objects.create(name='Profit and Loss Account', category=equity, code='E-PL', company=company, default=True)
    Account.objects.create(name='Opening Balance Equity', category=equity, code='E-OBE', company=company, default=True)

    # CREATE DEFAULT CATEGORIES AND LEDGERS FOR ASSETS

    assets = Category.objects.create(name='Assets', code='A', company=company, default=True)
    Category.objects.create(name='Other Receivables', code='A-OR', parent=assets, company=company, default=True)
    Category.objects.create(name='Tax Receivables', code='A-TR', parent=assets, company=company, default=True)
    Category.objects.create(name='Deferred Assets', code='A-DA', parent=assets, company=company, default=True)
    Category.objects.create(name='Fixed Assets', code='A-FA', parent=assets, company=company, default=True)
    Category.objects.create(name='Loans and Advances Given', code='A-L', parent=assets, company=company, default=True)
    Category.objects.create(name='Deposits Made', code='A-D', parent=assets, company=company, default=True)
    Category.objects.create(name='Employee', code='A-E', parent=assets, company=company, default=True)

    cash_account = Category.objects.create(name='Cash Accounts', code='A-C', parent=assets, company=company,
                                           default=True)
    Account.objects.create(company=company, default=True, name='Cash', category=cash_account, code='A-C-C')
    # Account.objects.create(name='Merchandise', category=assets, code='A-M', company=company, default=True)
    cash_equivalent_account = Category.objects.create(name='Cash Equivalent Account', code='A-CE', parent=assets,
                                                      company=company, default=True)
    # Account.objects.create(name='Cheque Account', category=cash_equivalent_account, code='A-CE-CQ', company=company,
    #                        default=True)

    bank_account = Category.objects.create(name='Bank Accounts', code='A-B', parent=assets, company=company,
                                           default=True)
    # Account(name='ATM Account', category=bank_account, code='A-B-A', company=company, default=True).save()
    # Account(name='Bank Account', category=bank_account, code='A-B-B', company=company, default=True).save()
    # Account(name='Card Account', category=bank_account, code='A-B-Ca', company=company, default=True).save()

    account_receivables = Category.objects.create(name='Account Receivables', code='A-AR', parent=assets,
                                                  company=company, default=True)
    Category.objects.create(name='Customers', code='A-AR-C', parent=account_receivables, company=company, default=True)

    employee_deductions = Category.objects.create(name='Employee Deductions', code='A-ED', parent=assets,
                                                  company=company, default=True)
    # Account.objects.create(name='Advances', category=employee_deductions, code='A-ED-AD', company=company, default=True)
    # Account.objects.create(name='Loans', category=employee_deductions, code='A-ED-L', company=company, default=True)
    # Account.objects.create(name='Payroll Taxes', category=employee_deductions, code='A-ED-T', company=company,
    #                        default=True)
    # Account.objects.create(name='Employees\' Contribution to Retirement Fund', category=employee_deductions,
    #                        code='A-ED-RF', company=company, default=True)
    # Account.objects.create(name='Compulsory Deductions', category=employee_deductions, code='A-ED-CD', company=company,
    #                        default=True)

    # CREATE DEFAULT CATEGORIES AND LEDGERS FOR LIABILITIES

    liabilities = Category.objects.create(name='Liabilities', code='L', company=company, default=True)
    account_payables = Category.objects.create(name='Account Payables', code='L-AP', parent=liabilities,
                                               company=company, default=True)
    Category.objects.create(name='Suppliers', parent=account_payables, code='L-AP-S', company=company, default=True)
    other_payables = Category.objects.create(name='Other Payables', code='L-OP', parent=liabilities, company=company,
                                             default=True)
    # Account.objects.create(name='Utility Bills Account', category=other_payables, code='L-OP-U', company=company,
    #                        default=True)
    Category.objects.create(name='Provisions', code='L-P', parent=liabilities, company=company, default=True)
    secured_loans = Category.objects.create(name='Secured Loans', code='L-SL', parent=liabilities, company=company,
                                            default=True)
    # Account.objects.create(name='Bank OD', category=secured_loans, code='L-SL-OD', company=company, default=True)
    # Account.objects.create(name='Bank Loans', category=secured_loans, code='L-SL-BL', company=company, default=True)
    Category.objects.create(name='Unsecured Loans', code='L-US', parent=liabilities, company=company, default=True)
    Category.objects.create(name='Deposits Taken', code='L-DT', parent=liabilities, company=company, default=True)
    Category.objects.create(name='Loans & Advances Taken', code='L-L&A', parent=liabilities, company=company,
                            default=True)
    duties_and_taxes = Category.objects.create(name='Duties & Taxes', code='L-T', parent=liabilities, company=company,
                                               default=True)
    # Account.objects.create(name='Sales Tax', category=duties_and_taxes, code='L-T-S', company=company, default=True)
    # Account.objects.create(name='Payroll Tax', category=duties_and_taxes, code='L-T-P', company=company, default=True)
    # Account.objects.create(name='Income Tax', category=duties_and_taxes, code='L-T-I', company=company, default=True)

    # CREATE DEFAULT CATEGORIES FOR INCOME

    income = Category.objects.create(name='Income', code='I', company=company, default=True)
    sales_category = Category.objects.create(name='Sales', code='I-S', parent=income, company=company, default=True)
    Account.objects.create(name='Sales Account', category=sales_category, company=company, default=True)
    direct_income = Category.objects.create(name='Direct Income', code='I-D', parent=income, company=company,
                                            default=True)
    Category.objects.create(name='Transfer and Remittance', code='I-D-T&R', parent=direct_income, company=company,
                            default=True)
    indirect_income = Category.objects.create(name='Indirect Income', code='I-II', parent=income, company=company,
                                              default=True)

    discount_income_category = Category.objects.create(name='Discount Income', parent=indirect_income,
                                                       company=company, default=True)
    Account.objects.create(name='Discount Income', category=discount_income_category, company=company, default=True)

    # CREATE DEFAULT CATEGORIES FOR EXPENSES

    expenses = Category.objects.create(name='Expenses', code='E', company=company, default=True)

    purchase_category = Category.objects.create(name='Purchase', code='E-P', parent=expenses, company=company, default=True)
    Account.objects.create(name='Purchase Account', category=purchase_category, company=company, default=True)

    direct_expenses = Category.objects.create(name='Direct Expenses', code='E-DE', parent=expenses, company=company,
                                              default=True)
    Category.objects.create(name='Purchase Expenses', code='E-DE-PE', parent=direct_expenses, company=company,
                            default=True)
    indirect_expenses = Category.objects.create(name='Indirect Expenses', code='E-IE', parent=expenses, company=company,
                                                default=True)
    Category.objects.create(name='Pay Head', code='E-IE-P', parent=indirect_expenses, company=company, default=True)
    discount_expense_category = Category.objects.create(name='Discount Expenses', parent=indirect_expenses,
                                                        company=company, default=True)
    Account.objects.create(name='Discount Expenses', category=discount_expense_category, company=company, default=True)

    # Opening Balance Difference

    # opening_balance_difference = Category.objects.create(name='Opening Balance Difference', code='O', company=company, default=True)
    # Account.objects.create(name='Opening Balance Difference', code='O-OBD', category=opening_balance_difference, company=company, default=True)


def get_account(request_or_company, name):
    if not request_or_company.__class__.__name__ == 'Company':
        company = request_or_company.company
    else:
        company = request_or_company
    if name in ['Purchase', 'Purchases']:
        return Account.objects.get(name='Purchase', category__name='Purchase', company=company)
    if name in ['Cash', 'Cash Account']:
        return Account.objects.get(name='Cash', category__name='Cash Accounts', company=company)


class TransactionModel(models.Model):
    @property
    def voucher_no(self):
        if hasattr(self, 'voucher_no'):
            return self.voucher_no
        if hasattr(self, 'voucher'):
            if hasattr(self.voucher, 'voucher_no'):
                return self.voucher.voucher_no
            else:
                return self.voucher_id
        return self.id

    def get_source_id(self):
        if hasattr(self, 'voucher_id'):
            return self.voucher_id
        return self.id

    def journal_entries(self):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = JournalEntry.objects.filter(content_type__app_label=app_label)
        if hasattr(self, 'rows'):
            row_ids = self.rows.values_list('id', flat=True)
            qs = qs.filter(
                Q(content_type__model=model + 'row', object_id__in=row_ids) | Q(content_type__model=model, object_id=self.id))
        else:
            qs = qs.filter(content_type__model=model, object_id=self.id)
        return qs

    def transactions(self):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = Transaction.objects.filter(journal_entry__content_type__app_label=app_label)
        if hasattr(self, 'rows'):
            row_ids = self.rows.values_list('id', flat=True)
            qs = qs.filter(Q(journal_entry__content_type__model=model + 'row', journal_entry__object_id__in=row_ids) | Q(
                journal_entry__content_type__model=model, journal_entry__object_id=self.id))
        else:
            qs = qs.filter(journal_entry__content_type__model=model, journal_entry__object_id=self.id)
        return qs

    class Meta:
        abstract = True


set_ledger_transactions = set_transactions
