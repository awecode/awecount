from auditlog.registry import auditlog
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.bank.models import BankAccount
from apps.ledger.models import Party, Account, set_transactions as set_ledger_transactions, get_account, JournalEntry, \
    TransactionModel
from apps.product.models import Item, Unit, set_inventory_transactions
from apps.tax.models import TaxScheme
from apps.users.models import Company, User, FiscalYear
from apps.voucher.base_models import InvoiceModel, InvoiceRowModel
from awecount.utils import get_next_voucher_no

STATUSES = (
    ('Draft', 'Draft'),
    ('Issued', 'Issued'),
    ('Cancelled', 'Cancelled'),
    ('Paid', 'Paid'),
    # TODO create partial payment system
    ('Partially Paid', 'Partially Paid'),
)
MODES = (
    ('Credit', 'Credit'),
    ('Cash', 'Cash'),
    ('Bank Deposit', 'Bank Deposit'),
)

DISCOUNT_TYPES = (
    ('Amount', 'Amount'),
    ('Percent', 'Percent'),
)


class Discount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=25, choices=DISCOUNT_TYPES)
    value = models.FloatField()
    trade_discount = models.BooleanField(default=True)

    def __str__(self):
        if self.name:
            return self.name
        return '{} - {}'.format(self.type, self.value)

    class Meta:
        abstract = True


class SalesDiscount(Discount):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_discounts')


class PurchaseDiscount(Discount):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='purchase_discounts')


class SalesVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    issue_datetime = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    due_date = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)

    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='sales')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    remarks = models.TextField(blank=True, null=True)
    is_export = models.BooleanField(default=False)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_vouchers')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_vouchers')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='sales_vouchers')

    class Meta:
        unique_together = ('company', 'voucher_no', 'fiscal_year')

    @property
    def buyer_name(self):
        if self.party_id:
            return self.party.name
        return self.customer_name


    def apply_inventory_transactions(self):
        for row in self.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related('item__account'):
            set_inventory_transactions(
                row,
                self.date,
                ['cr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self):
        if self.status == 'Cancelled':
            self.apply_cancel_transaction()
            return
        if self.status == 'Draft':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == 'Credit':
            dr_acc = self.party.customer_account
        elif self.mode == 'Cash':
            dr_acc = get_account(self.company, 'Cash')
            self.status = 'Paid'
        elif self.mode == 'Bank Deposit':
            dr_acc = self.bank_account.ledger
            self.status = 'Paid'
        else:
            raise ValueError('No such mode!')

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(sub_total_after_row_discounts)

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_allowed_ledger',
                                                     'item__sales_ledger'):
            entries = []

            row_total = row.quantity * row.rate
            sales_value = row_total + 0

            row_discount = 0
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= row_discount_amount
                if trade_discount:
                    sales_value -= row_discount_amount
                else:
                    row_discount += row_discount_amount

            if dividend_discount > 0:
                row_dividend_discount = (row_total / sub_total_after_row_discounts) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    sales_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(['dr', row.item.discount_allowed_ledger, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['cr', row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['cr', row.item.sales_ledger, sales_value])
            entries.append(['dr', dr_acc, row_total])

            set_ledger_transactions(row, self.date, *entries, clear=True)
        self.apply_inventory_transactions()

    def save(self, *args, **kwargs):
        if self.status not in ['Draft', 'Cancelled'] and not self.voucher_no:
            raise ValueError('Issued invoices need a voucher number!')
        super().save(*args, **kwargs)


class SalesVoucherRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(SalesVoucher, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='sales_rows')
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='sales_rows')


class PurchaseVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveIntegerField()
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='purchases')

    remarks = models.TextField(blank=True, null=True)
    is_import = models.BooleanField(default=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_vouchers')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='purchase_vouchers')

    def apply_inventory_transaction(self):
        for row in self.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related('item__account'):
            set_inventory_transactions(
                row,
                self.date,
                ['dr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self):
        if self.status == 'Cancelled':
            self.apply_cancel_transaction()
            return
        if self.status == 'Draft':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == 'Credit':
            cr_acc = self.party.supplier_account
        elif self.mode == 'Cash':
            cr_acc = get_account(self.company, 'Cash')
            self.status = 'Paid'
        elif self.mode == 'Bank Deposit':
            cr_acc = self.bank_account.ledger
            self.status = 'Paid'
        else:
            raise ValueError('No such mode!')

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(sub_total_after_row_discounts)

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_received_ledger',
                                                     'item__purchase_ledger'):
            entries = []

            row_total = row.quantity * row.rate
            purchase_value = row_total + 0

            row_discount = 0
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= row_discount_amount
                if trade_discount:
                    purchase_value -= row_discount_amount
                else:
                    row_discount += row_discount_amount

            if dividend_discount > 0:
                row_dividend_discount = (row_total / sub_total_after_row_discounts) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    purchase_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(['cr', row.item.discount_received_ledger, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['dr', row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['dr', row.item.purchase_ledger, purchase_value])
            entries.append(['cr', cr_acc, row_total])
            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()


class PurchaseVoucherRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(PurchaseVoucher, related_name='rows', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='purchases', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='purchase_rows')
    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.item.cost_price:
            self.item.cost_price = self.rate
            self.item.save()
        super().save(*args, **kwargs)


CREDIT_NOTE_STATUSES = (
    ('Draft', 'Draft'),
    ('Issued', 'Issued'),
    ('Cancelled', 'Cancelled'),
    ('Resolved', 'Resolved'),
)


class CreditNote(TransactionModel, InvoiceModel):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0])

    invoices = models.ManyToManyField(SalesVoucher, related_name='credit_notes')

    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='credit_notes')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    remarks = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_notes')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='credit_notes')
    print_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('company', 'voucher_no', 'fiscal_year')

    def apply_inventory_transaction(voucher):
        for row in voucher.rows.filter(is_returned=True).filter(
                        Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related('item__account'):
            set_inventory_transactions(
                row,
                voucher.date,
                ['dr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self):
        if self.status == 'Cancelled':
            self.apply_cancel_transaction()
            return
        if self.status == 'Draft':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == 'Credit':
            cr_acc = self.party.customer_account
        elif self.mode == 'Cash':
            cr_acc = get_account(self.company, 'Cash')
            self.status = 'Resolved'
        elif self.mode == 'Bank Deposit':
            cr_acc = self.bank_account.ledger
            self.status = 'Resolved'
        else:
            raise ValueError('No such mode!')

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(sub_total_after_row_discounts)

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_allowed_ledger',
                                                     'item__sales_ledger'):
            entries = []

            row_total = row.quantity * row.rate
            sales_value = row_total + 0

            row_discount = 0
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= row_discount_amount
                if trade_discount:
                    sales_value -= row_discount_amount
                else:
                    row_discount += row_discount_amount

            if dividend_discount > 0:
                row_dividend_discount = (row_total / sub_total_after_row_discounts) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    sales_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(['dr', row.item.discount_allowed_ledger, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['dr', row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['dr', row.item.sales_ledger, sales_value])
            entries.append(['cr', cr_acc, row_total])

            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()

    def __str__(self):
        return str(self.voucher_no) + '- ' + self.party.name


class CreditNoteRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(CreditNote, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='credit_note_rows')
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='credit_note_rows')


class DebitNote(TransactionModel, InvoiceModel):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0])

    invoices = models.ManyToManyField(PurchaseVoucher, related_name='debit_notes')

    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='debit_notes')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    remarks = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debit_notes')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='debit_notes')
    print_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('company', 'voucher_no', 'fiscal_year')

    def apply_inventory_transaction(self):
        for row in self.rows.filter(is_returned=True).filter(
                        Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related('item__account'):
            set_inventory_transactions(
                row,
                self.date,
                ['cr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self):
        if self.status == 'Cancelled':
            self.apply_cancel_transaction()
            return
        if self.status == 'Draft':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == 'Credit':
            dr_acc = self.party.supplier_account
        elif self.mode == 'Cash':
            dr_acc = get_account(self.company, 'Cash')
            self.status = 'Resolved'
        elif self.mode == 'Bank Deposit':
            dr_acc = self.bank_account.ledger
            self.status = 'Resolved'
        else:
            raise ValueError('No such mode!')

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(sub_total_after_row_discounts)

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_received_ledger',
                                                     'item__purchase_ledger'):
            entries = []

            row_total = row.quantity * row.rate
            purchase_value = row_total + 0

            row_discount = 0
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= row_discount_amount
                if trade_discount:
                    purchase_value -= row_discount_amount
                else:
                    row_discount += row_discount_amount

            if dividend_discount > 0:
                row_dividend_discount = (row_total / sub_total_after_row_discounts) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    purchase_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(['cr', row.item.discount_received_ledger, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['cr', row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['cr', row.item.purchase_ledger, purchase_value])
            entries.append(['dr', dr_acc, row_total])
            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()


class DebitNoteRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(DebitNote, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='debit_note_rows')
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='debit_note_rows')
    

class InvoiceDesign(models.Model):
    design = models.ImageField(upload_to='design/')
    canvas = models.TextField()
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='invoice')

    def __str__(self):
        return self.company.name + ' ' + 'Invoice'


class JournalVoucher(models.Model):
    STATUSES = [('Cancelled', 'Cancelled'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved')]

    voucher_no = models.IntegerField()
    date = models.DateField()
    narration = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSES, default='Unapproved')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('company', 'voucher_no')

    def __init__(self, *args, **kwargs):
        super(JournalVoucher, self).__init__(*args, **kwargs)
        if not self.pk and not self.voucher_no:
            self.voucher_no = get_next_voucher_no(JournalVoucher, self.company_id)

    def get_total_dr_amount(self):
        total_dr_amount = 0
        for o in self.rows.all():
            total_dr_amount += o.dr_amount
        return total_dr_amount

    def get_total_cr_amount(self):
        total_cr_amount = 0
        for o in self.rows.all():
            total_cr_amount += o.cr_amount
        return total_cr_amount

    def get_voucher_no(self):
        return self.voucher_no

    @staticmethod
    def apply_transactions(voucher):
        if voucher.status == 'Cancelled':
            voucher.apply_cancel_transaction()
            return
        if not voucher.status == 'Approved':
            return

        entries = []
        # filter bypasses rows cached by prefetching
        for row in voucher.rows.filter():
            amount = row.dr_amount if row.type == 'Dr' else row.cr_amount
            entries.append([row.type.lower(), row.account, amount])
        set_ledger_transactions(voucher, voucher.date, *entries, clear=True)
        return

    @staticmethod
    def apply_cancel_transaction(self):
        content_type = ContentType.objects.get(model='journalvoucher')
        row_ids = self.rows.values_list('id', flat=True)
        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()


class JournalVoucherRow(models.Model):
    types = [('Dr', 'Dr'), ('Cr', 'Cr')]
    type = models.CharField(choices=types, default='Dr', max_length=2)
    account = models.ForeignKey(Account, related_name='account_rows', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    dr_amount = models.FloatField(null=True, blank=True)
    cr_amount = models.FloatField(null=True, blank=True)
    journal_voucher = models.ForeignKey(JournalVoucher, related_name='rows', on_delete=models.CASCADE)

    def get_voucher_no(self):
        return self.journal_voucher.voucher_no


auditlog.register(SalesVoucher)
auditlog.register(SalesVoucherRow)
auditlog.register(PurchaseVoucher)
auditlog.register(PurchaseVoucherRow)
