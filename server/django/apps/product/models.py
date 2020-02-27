from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models, IntegrityError, transaction
from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.ledger.models import Account, Category as AccountCategory
from apps.tax.models import TaxScheme
from apps.users.models import Company
from awecount.utils import none_for_zero, zero_for_none


class Unit(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    @staticmethod
    def create_default_units(company):
        units = [
            Unit(name='Piece(s)', short_name='pcs', company=company),
            Unit(name='Unit(s)', short_name='unit', company=company),
        ]
        return Unit.objects.bulk_create(units)

    def __str__(self):
        return self.short_name or self.name

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('short_name', 'company')


LEDGER_TYPES = (
    ('dedicated', 'Use Dedicated Ledger'),
    ('category', 'Use Category\'s Ledger'),
    ('global', 'Use Global Ledger'),
)

ITEM_TYPES = (
    ('Tangible Sellable', 'Tangible Sellable'),
    ('Intangible Sellable', 'Intangible Sellable'),
    ('Expense', 'Expense'),
    ('Asset', 'Asset'),
)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='brands')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    default_unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    default_tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, related_name='categories',
                                           on_delete=models.SET_NULL)

    sales_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                      related_name='sales_categories')
    purchase_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                         related_name='purchase_categories')
    discount_allowed_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                 related_name='discount_allowed_categories')
    discount_received_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                  related_name='discount_received_categories')

    sales_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                               related_name='sales_item_categories')
    purchase_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                  related_name='purchase_item_categories')
    discount_allowed_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                          related_name='discount_allowed_item_categories')
    discount_received_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                           related_name='discount_received_item_categories')
    fixed_asset_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                     related_name='fixed_asset_account_category')
    direct_expense_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                        related_name='direct_expense_account_category')
    indirect_expense_account_category = models.ForeignKey(AccountCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                                          related_name='indirect_expense_account_category')

    items_sales_account_type = models.CharField(max_length=100, choices=LEDGER_TYPES, default='dedicated')
    items_purchase_account_type = models.CharField(max_length=100, choices=LEDGER_TYPES, default='dedicated')
    items_discount_allowed_account_type = models.CharField(max_length=100, choices=LEDGER_TYPES, default='dedicated')
    items_discount_received_account_type = models.CharField(max_length=100, choices=LEDGER_TYPES, default='dedicated')

    # type = models.CharField(max_length=20, choices=ITEM_TYPES)
    track_inventory = models.BooleanField(default=True)
    can_be_sold = models.BooleanField(default=True)
    can_be_purchased = models.BooleanField(default=True)
    fixed_asset = models.BooleanField(default=False)
    direct_expense = models.BooleanField(default=False)
    indirect_expense = models.BooleanField(default=False)

    extra_fields = JSONField(default=list, null=True, blank=True)
    # {'name': 'Author', 'type': 'Text/Number/Date/Long Text', 'enable_search': 'false/true'}

    use_account_subcategory = models.BooleanField(default=False)
    account_category = models.ForeignKey(AccountCategory, blank=True, null=True, related_name='item_categories',
                                         on_delete=models.SET_NULL)

    # Required for module-wise permission check
    key = 'InventoryCategory'

    def get_account_category(self, default_category_name, prefix=''):
        if self.use_account_subcategory and self.account_category_id and self.account_category:
            name = self.name
            if prefix:
                name = '{} - {}'.format(prefix, name)
            account_category = AccountCategory(name=name, company=self.company)
            account_category.set_parent(self.account_category)
            code = account_category.suggest_code(self, prefix='C')
            try:
                account_category.save()
            except IntegrityError:
                account_category = AccountCategory.objects.get(code=code, company=self.company)
        else:
            account_category = self.account_category or AccountCategory.objects.get(name=default_category_name, default=True,
                                                                                    company=self.company)
        return account_category

    def save(self, *args, **kwargs):
        self.validate_unique()

        post_save = kwargs.pop('post_save', True)
        super().save(*args, **kwargs)

        if post_save:
            if not self.sales_account:
                ledger = Account(name=self.name + ' (Sales)', company=self.company)
                ledger.add_category('Sales')
                ledger.suggest_code(self, prefix='C')
                ledger.save()
                self.sales_account = ledger
            if not self.purchase_account:
                ledger = Account(name=self.name + ' (Purchase)', company=self.company)
                ledger.add_category('Purchase')
                ledger.suggest_code(self, prefix='C')
                ledger.save()
                self.purchase_account = ledger
            if not self.discount_allowed_account:
                discount_allowed_account = Account(name='Discount Allowed - ' + self.name, company=self.company)
                discount_allowed_account.add_category('Discount Expenses')
                discount_allowed_account.suggest_code(self, prefix='C')
                discount_allowed_account.save()
                self.discount_allowed_account = discount_allowed_account
            if not self.discount_received_account:
                discount_received_account = Account(name='Discount Received - ' + self.name, company=self.company)
                discount_received_account.add_category('Discount Income')
                discount_received_account.suggest_code(self, prefix='C')
                discount_received_account.save()
                self.discount_received_account = discount_received_account

            # Set/Update account categories

            if self.can_be_sold:
                account_category = self.get_account_category('Sales', prefix='Sales')
                self.sales_account_category = account_category
                Account.objects.filter(sales_item__category=self).update(category=account_category)
                account_category = self.get_account_category('Discount Expenses', prefix='Discount Allowed')
                self.discount_allowed_account_category = account_category
                Account.objects.filter(discount_allowed_item__category=self).update(category=account_category)

            if self.can_be_purchased:
                account_category = self.get_account_category('Purchase', prefix='Purchase')
                self.purchase_account_category = account_category
                Account.objects.filter(purchase_item__category=self).update(category=account_category)
                account_category = self.get_account_category('Discount Income', prefix='Discount Received')
                self.discount_received_account_category = account_category
                Account.objects.filter(discount_allowed_item__category=self).update(category=account_category)

            if self.direct_expense:
                account_category = self.get_account_category('Direct Expenses')
                self.direct_expense_account_category = account_category
                Account.objects.filter(expense_item__category=self).update(category=account_category)
            elif self.indirect_expense:
                account_category = self.get_account_category('Indirect Expenses')
                self.indirect_expense_account_category = account_category
                Account.objects.filter(expense_item__category=self).update(category=account_category)
            elif self.fixed_asset:
                account_category = self.get_account_category('Fixed Assets')
                self.fixed_asset_account_category = account_category
                Account.objects.filter(fixed_asset_item__category=self).update(category=account_category)

            if self.use_account_subcategory and self.account_category_id and self.account_category:
                with transaction.atomic():
                    # TODO Slow
                    AccountCategory.objects.rebuild()

            self.save(post_save=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = (('code', 'company'), ('name', 'company'))


class InventoryAccount(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    account_no = models.PositiveIntegerField(blank=True, null=True)
    current_balance = models.FloatField(default=0)
    opening_balance = models.FloatField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inventory')

    def __str__(self):
        return self.name

    @staticmethod
    def get_next_account_no():
        from django.db.models import Max

        max_voucher_no = InventoryAccount.objects.all().aggregate(Max('account_no'))['account_no__max']
        if max_voucher_no:
            return max_voucher_no + 1
        else:
            return 1

    def get_category(self):
        try:
            item = self.item
        except:
            return None
        try:
            category = item.category
        except:
            return None
        return category

    def save(self, *args, **kwargs):
        if not self.account_no:
            self.account_no = self.get_next_account_no()
        super().save(*args, **kwargs)


class JournalEntry(models.Model):
    date = models.DateField()
    content_type = models.ForeignKey(ContentType, related_name='inventory_journal_entries', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def get_for(source):
        try:
            return JournalEntry.objects.get(content_type=ContentType.objects.get_for_model(source), object_id=source.id)
        except JournalEntry.DoesNotExist:
            return None

    def __str__(self):
        return str(self.content_type) + ': ' + str(self.object_id) + ' [' + str(self.date) + ']'

    class Meta:
        verbose_name_plural = u'Inventory Journal Entries'


class Transaction(models.Model):
    account = models.ForeignKey(InventoryAccount, on_delete=models.CASCADE)
    dr_amount = models.FloatField(null=True, blank=True)
    cr_amount = models.FloatField(null=True, blank=True)
    current_balance = models.FloatField(null=True, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, related_name='transactions', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.account) + ' [' + str(self.dr_amount) + ' / ' + str(self.cr_amount) + ']'

    def total_dr_amount(self):
        dr_transctions = Transaction.objects.filter(account__name=self.account.name, cr_amount=None,
                                                    journal_entry__journal__rate=self.journal_entry.source.rate)
        total = 0
        for transaction in dr_transctions:
            total += transaction.dr_amount
        return total

    def total_dr_amount_without_rate(self):
        dr_transctions = Transaction.objects.filter(account__name=self.account.name, cr_amount=None)
        total = 0
        for transaction in dr_transctions:
            total += transaction.dr_amount
        return total

    def get_balance(self):
        return zero_for_none(self.dr_amount) - zero_for_none(self.cr_amount)


def alter(account, date, diff):
    Transaction.objects.filter(journal_entry__date__gt=date, account=account).update(
        current_balance=none_for_zero(zero_for_none(F('current_balance')) + zero_for_none(diff)))


@receiver(pre_delete, sender=Transaction)
def _transaction_delete(sender, instance, **kwargs):
    transaction = instance
    if transaction.dr_amount:
        transaction.account.current_balance -= transaction.dr_amount

    if transaction.cr_amount:
        transaction.account.current_balance += transaction.cr_amount

    diff = float(zero_for_none(transaction.dr_amount)) - float(zero_for_none(transaction.cr_amount))
    alter(transaction.account, transaction.journal_entry.date, diff)

    transaction.account.save()


def set_inventory_transactions(model, date, *args):
    args = [arg for arg in args if arg is not None]
    journal_entry, created = JournalEntry.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(model), object_id=model.id,
        defaults={
            'date': date
        })

    for arg in args:
        matches = journal_entry.transactions.filter(account=arg[1])
        diff = 0
        if not matches:
            transaction = Transaction()
        else:
            transaction = matches[0]
            diff = zero_for_none(transaction.cr_amount)
            diff -= zero_for_none(transaction.dr_amount)
        if arg[0] == 'dr':
            transaction.dr_amount = float(arg[2])
            transaction.cr_amount = None
            diff += float(arg[2])
        elif arg[0] == 'cr':
            transaction.cr_amount = float(arg[2])
            transaction.dr_amount = None
            diff -= float(arg[2])
        elif arg[0] == 'ob':
            transaction.dr_amount = float(arg[2])
            transaction.cr_amount = None
            diff += float(arg[2])
        else:
            raise Exception('Transactions can only be either "dr" or "cr".')
        transaction.account = arg[1]
        if isinstance(transaction.account.current_balance, str):
            transaction.account.current_balance = float(transaction.account.current_balance)
        transaction.account.current_balance += diff
        transaction.current_balance = transaction.account.current_balance
        transaction.account.save()
        journal_entry.transactions.add(transaction, bulk=False)
        alter(transaction.account, date, diff)


class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name='items')
    description = models.TextField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)

    front_image = models.ImageField(blank=True, null=True, upload_to='item_front_images/')
    back_image = models.ImageField(blank=True, null=True, upload_to='item_back_images/')

    brand = models.ForeignKey(Brand, blank=True, null=True, related_name='items', on_delete=models.SET_NULL)

    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, related_name='items', on_delete=models.SET_NULL)

    account = models.OneToOneField(InventoryAccount, related_name='item', null=True, on_delete=models.CASCADE)

    sales_account = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='sales_item')
    purchase_account = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='purchase_item')
    discount_allowed_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                 related_name='discount_allowed_item')
    discount_received_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                  related_name='discount_received_item')
    expense_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                        related_name='expense_item')
    fixed_asset_account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                            related_name='fixed_asset_item')

    track_inventory = models.BooleanField(default=True)
    can_be_sold = models.BooleanField(default=True)
    can_be_purchased = models.BooleanField(default=True)
    fixed_asset = models.BooleanField(default=False)
    direct_expense = models.BooleanField(default=False)
    indirect_expense = models.BooleanField(default=False)

    extra_data = JSONField(null=True, blank=True)
    search_data = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def expense(self):
        return self.direct_expense or self.indirect_expense

    @property
    def is_trackable(self):
        return self.track_inventory or self.fixed_asset

    @property
    def dr_account(self):
        if self.expense:
            return self.expense_account
        if self.fixed_asset:
            return self.fixed_asset_account
        return self.purchase_account

    def save(self, *args, **kwargs):
        self.validate_unique()

        post_save = kwargs.pop('post_save', True)
        super().save(*args, **kwargs)
        if post_save:
            if self.can_be_sold and not self.sales_account_id:
                account = Account(name=self.name + ' (Sales)', company=self.company)
                if self.category and self.category.sales_account_category_id:
                    account.category = self.category.sales_account_category
                else:
                    account.add_category('Sales')
                account.suggest_code(self)
                account.save()
                self.sales_account = account
            if self.can_be_purchased and not self.purchase_account_id:
                account = Account(name=self.name + ' (Purchase)', company=self.company)
                if self.category and self.category.purchase_account_category_id:
                    account.category = self.category.purchase_account_category
                else:
                    account.add_category('Purchase')
                account.suggest_code(self)
                account.save()
                self.purchase_account = account
            if self.can_be_sold and not self.discount_allowed_account_id:
                discount_allowed_account = Account(name='Discount Allowed ' + self.name, company=self.company)
                if self.category and self.category.discount_allowed_account_category_id:
                    discount_allowed_account.category = self.category.discount_allowed_account_category
                else:
                    discount_allowed_account.add_category('Discount Expenses')
                discount_allowed_account.suggest_code(self)
                discount_allowed_account.save()
                self.discount_allowed_account = discount_allowed_account

            if (self.can_be_purchased or self.fixed_asset or self.expense) and not self.discount_received_account_id:
                discount_received_acc = Account(name='Discount Received ' + self.name, company=self.company)
                if self.category and self.category.discount_received_account_category_id:
                    discount_received_acc.category = self.category.discount_received_account_category
                else:
                    discount_received_acc.add_category('Discount Income')
                discount_received_acc.suggest_code(self)
                discount_received_acc.save()
                self.discount_received_account = discount_received_acc

            if (self.direct_expense or self.indirect_expense) and not self.expense_account_id:
                expense_account = Account(name=self.name, company=self.company)
                if self.direct_expense:
                    if self.category and self.category.direct_expense_account_category_id:
                        expense_account.category = self.category.direct_expense_account_category
                    else:
                        expense_account.add_category('Direct Expenses')
                else:
                    if self.category and self.category.indirect_expense_account_category_id:
                        expense_account.category = self.category.indirect_expense_account_category
                    else:
                        expense_account.add_category('Indirect Expenses')
                expense_account.suggest_code(self)
                expense_account.save()
                self.expense_account = expense_account

            if self.fixed_asset and not self.fixed_asset_account_id:
                fixed_asset_account = Account(name=self.name, company=self.company)
                if self.category and self.category.fixed_asset_account_category_id:
                    fixed_asset_account.category = self.category.fixed_asset_account_category
                else:
                    fixed_asset_account.add_category('Fixed Assets')
                fixed_asset_account.suggest_code(self)
                fixed_asset_account.save()
                self.fixed_asset_account = fixed_asset_account

            if not self.account_id and (self.track_inventory or self.fixed_asset):
                account = InventoryAccount(code=self.code, name=self.name, company_id=self.company_id)
                account.save()
                self.account = account

            if self.category and self.category.extra_fields:
                search_data = []
                for field in self.category.extra_fields:
                    if type(field) in [dict, OrderedDict]:
                        if field.get('enable_search'):
                            if type(self.extra_data) in [dict, OrderedDict]:
                                search_data.append(str(self.extra_data.get(field.get('name'))))

                search_text = ', '.join(search_data)
                self.search_data = search_text

            # prevents recursion
            self.save(post_save=False)

    class Meta:
        unique_together = ('code', 'company',)
