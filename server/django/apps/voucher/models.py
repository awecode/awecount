from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.bank.models import BankAccount
from apps.ledger.models import Party, Account, set_transactions as set_ledger_transactions, get_account, JournalEntry
from apps.product.models import Item, Unit
from apps.tax.models import TaxScheme
from apps.users.models import Company, User
from awecount.utils import get_next_voucher_no, wGenerator
from awecount.utils.nepdate import ad2bs, string_from_tuple

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
    ('Cheque', 'Cheque'),
    ('ePayment', 'ePayment'),
    ('Bank Deposit', 'Bank Deposit'),
)

DISCOUNT_TYPES = (
    ('Amount', 'Amount'),
    ('Percent', 'Percent'),
)


class SalesVoucher(models.Model):
    voucher_no = models.PositiveSmallIntegerField()
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    issue_datetime = models.DateTimeField(default=timezone.now)
    transaction_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_vouchers')
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)
    remarks = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    total_amount = models.FloatField(null=True, blank=True)  #
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    epayment = models.CharField(max_length=50, blank=True, null=True)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_vouchers')

    def __str__(self):
        return str(self.voucher_no)

    def get_billed_to(self):
        return self.party.name if self.party else self.customer_name

    @property
    def date(self):
        return self.transaction_date.strftime('%m-%b-%Y')

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.total_amount)

    @property
    def bs_date(self):
        return string_from_tuple(ad2bs(self.transaction_date.strftime('%Y-%m-%d')))

    def get_vat(self):
        tax_scheme = []
        vat = 0
        for row in self.rows.all():
            if row.tax_scheme:
                tax_object = row.tax_scheme
                tax_scheme.append(tax_object.name)
                vat = vat + row.tax_amount
        tax_text = 'TAX'
        if tax_scheme and len(set(tax_scheme)) == 1:
            tax_text = tax_scheme[0]
        return tax_text, vat

    def get_sub_total(self):
        total = 0
        for row in self.rows.all():
            total += row.total
        return total

    @property
    def discount_amount(self):
        discount = 0
        if self.discount and self.discount_type == 'Amount':
            discount = self.discount
        elif self.discount and self.discount_type == 'Percent':
            discount = self.get_sub_total() * (self.discount / 100)
        return discount

    def apply_cancel_transaction(self):
        content_type = ContentType.objects.get(model='salesvoucherrow')
        row_ids = [row.id for row in self.rows.all()]
        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()

    def apply_mark_as_paid(self):
        today = timezone.now().today()
        entries = []
        total = self.total_amount
        cash_account = get_account(self.company, 'Cash')
        entries.append(['cr', self.party.customer_account, total])
        entries.append(['dr', cash_account, total])
        set_ledger_transactions(self, today, *entries)

    @staticmethod
    def apply_transactions(voucher):
        # entries = []
        if voucher.status == 'Cancelled':
            voucher.apply_cancel_transaction()
        if not voucher.status == 'Issued':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if voucher.mode == 'Credit':
            dr_acc = voucher.party.customer_account
        elif voucher.mode == 'Cash':
            dr_acc = get_account(voucher.company, 'Cash')
            voucher.status = 'Paid'
        # TODO Allow creating cheque deposit
        elif voucher.mode == 'Cheque':
            dr_acc = voucher.party.customer_account
            voucher.status = 'Paid'
        elif voucher.mode == 'Bank Deposit':
            dr_acc = voucher.bank_account.ledger
            voucher.status = 'Paid'
        # elif voucher.mode == 'ePayment':
        #     pass

        voucher.save()

        dividend_discount = 0

        if voucher.discount > 0 and voucher.discount_type:
            dividend_discount = voucher.discount_amount

        for row in voucher.rows.all():
            entries = []

            pure_total = row.quantity * row.rate
            # if tax inclusive, reduce tax from pure_total to get the real pure_total
            row_total = pure_total

            entries.append(['cr', row.item.sales_ledger, pure_total])

            if row.tax_scheme:
                row_tax_amount = row.tax_amount
                entries.append(['cr', row.tax_scheme.payable, row_tax_amount])
                row_total += row_tax_amount

            row_discount = 0
            if dividend_discount > 0:
                row_discount = (pure_total / voucher.get_sub_total()) * dividend_discount
            if row.discount > 0:
                row_discount += row.discount_amount
            if row_discount > 0:
                entries.append(['dr', row.item.discount_allowed_ledger, row_discount])
                row_total += row_discount

            entries.append(['dr', dr_acc, row_total])

            set_ledger_transactions(row, voucher.transaction_date, *entries, clear=True)
        # Following set_ledger transactions stays outside for loop
        # set_ledger_transactions(voucher, voucher.transaction_date, *entries, clear=True)


class SalesVoucherRow(models.Model):
    voucher = models.ForeignKey(SalesVoucher, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='sales_rows')

    def __str__(self):
        return str(self.voucher.voucher_no)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher.id

    @property
    def discount_amount(self):
        discount = 0
        if self.discount and self.discount_type == 'Amount':
            discount = self.discount
        elif self.discount and self.discount_type == 'Percent':
            sub_total = self.quantity * self.rate
            discount = sub_total * (self.discount / 100)
        return discount

    @property
    def tax_amount(self):
        amount = 0
        if self.tax_scheme:
            tax_object = self.tax_scheme
            amount = (tax_object.rate / 100) * self.total
        return amount

    @property
    def total(self):
        sub_total = self.quantity * self.rate
        if self.discount and self.discount_type:
            if self.discount_type == 'Amount':
                sub_total = sub_total - self.discount
            elif self.discount_type == 'Percent':
                sub_total = sub_total - (sub_total * (self.discount / 100))
        return sub_total


class PurchaseVoucher(models.Model):
    tax_choices = [('No Tax', 'No Tax'), ('Tax Inclusive', 'Tax Inclusive'), ('Tax Exclusive', 'Tax Exclusive'), ]
    voucher_no = models.PositiveIntegerField(blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    credit = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    tax = models.CharField(max_length=10, choices=tax_choices, default='inclusive', null=True, blank=True)
    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, on_delete=models.CASCADE)
    due_date = models.DateField(blank=True, null=True)
    pending_amount = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def type(self):
        return 'Credit' if self.credit else 'Cash'

    def __init__(self, *args, **kwargs):
        super(PurchaseVoucher, self).__init__(*args, **kwargs)

        if not self.pk and not self.voucher_no:
            self.voucher_no = get_next_voucher_no(PurchaseVoucher, self.company_id)

    @property
    def voucher_type(self):
        return 'PurchaseVoucher'

    @property
    def row_discount_total(self):
        grand_total = 0
        # for obj in self.rows.all():
        #     total = obj.quantity * obj.rate
        #     discount = get_discount_with_percent(total, obj.discount)
        #     grand_total += discount
        return grand_total


class PurchaseVoucherRow(models.Model):
    voucher = models.ForeignKey(PurchaseVoucher, related_name='rows', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='purchases', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.item.cost_price = self.rate
        self.item.save()
        super(PurchaseVoucherRow, self).save(*args, **kwargs)

    def get_source_id(self):
        return self.voucher.id

    def get_voucher_no(self):
        return self.voucher.voucher_no


class CreditVoucher(models.Model):
    voucher_no = models.PositiveSmallIntegerField()
    party = models.ForeignKey(Party, verbose_name='Receipt From', on_delete=models.CASCADE)
    date = models.DateField()
    reference = models.CharField(max_length=50, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    description = models.TextField()
    receipt = models.ForeignKey(Account, blank=True, null=True, related_name="cash_receipt", on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sale_vouchers = models.ManyToManyField(SalesVoucher, related_name='credit_notes')

    def __init__(self, *args, **kwargs):
        super(CreditVoucher, self).__init__(*args, **kwargs)
        if not self.pk and not self.voucher_no:
            self.voucher_no = get_next_voucher_no(CreditVoucher, self.company_id)

    @staticmethod
    def apply_transactions(voucher):
        cash_account = get_account(voucher.company, 'Cash')
        set_ledger_transactions(voucher, voucher.date,
                                ['dr', cash_account, voucher.amount],
                                ['cr', voucher.party.customer_account, voucher.amount]
                                )
        return

    @property
    def total(self):
        grand_total = 0
        for obj in self.rows.all():
            total = obj.receipt
            grand_total += total
        return grand_total

    def get_voucher_no(self):
        return self.voucher_no

    def get_absolute_url(self):
        return 'url'

    def __str__(self):
        return str(self.voucher_no) + '- ' + self.party.name


class CreditVoucherRow(models.Model):
    # invoice = models.ForeignKey(SalesVoucher, related_name='receipts', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    # receipt = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    credit_amount = models.FloatField(blank=True, null=True)
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='credit_rows')
    cash_receipt = models.ForeignKey(CreditVoucher, related_name='rows', on_delete=models.CASCADE)

    def get_voucher_no(self):
        return self.cash_receipt.voucher_no

    def get_absolute_url(self):
        return 'url'
        # return reverse_lazy('credit_voucher_edit', kwargs={'pk': self.cash_receipt_id})

        # def overdue_days(self):
        #     if self.invoice.due_date and self.invoice.due_date < date.today():
        #         overdue_days = date.today() - self.invoice.due_date
        #         return overdue_days.days
        #     return ''

        # class Meta:
        #     unique_together = ('invoice', 'cash_receipt')


class Bank(models.Model):
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BankBranch(models.Model):
    location = models.CharField(max_length=255)
    bank = models.ForeignKey(Bank, related_name='branches', on_delete=models.CASCADE)
    start_cheque_no = models.IntegerField(default=0)
    current_cheque_no = models.IntegerField(blank=True, null=True)
    cheque_prefix = models.CharField(max_length=10, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def increase_cheque_no(self):
        self.current_cheque_no = self.get_cheque_no()
        self.save()

    def get_cheque_no(self):
        cheque_no = self.current_cheque_no if self.current_cheque_no else self.start_cheque_no
        return cheque_no + 1

    @property
    def name(self):
        bank_name = self.bank.short_name or self.bank.name
        _name = '{} {}'.format(bank_name, self.location)
        return _name

    def __str__(self):
        return "{}: {}".format(self.bank.name, self.location)

    class Meta:
        verbose_name_plural = 'Bank branches'


class ChequeVoucher(models.Model):
    cheque_no = models.CharField(max_length=100, null=True, blank=True)
    bank_branch = models.ForeignKey(BankBranch, blank=True, null=True, on_delete=models.PROTECT)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="cheques")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.bank_branch.increase_cheque_no()
        super(ChequeVoucher, self).save(*args, **kwargs)

    def __str__(self):
        return self.date.strftime('%d-%m-%Y') + ': ' + str(self.user)

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.amount)


class InvoiceDesign(models.Model):
    design = models.ImageField(upload_to='design/')
    canvas = models.TextField()
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='invoice')

    def __str__(self):
        return self.company.name + ' ' + 'Invoice'


class JournalVoucher(models.Model):
    voucher_no = models.IntegerField()
    date = models.DateField()
    narration = models.TextField()
    statuses = [('Cancelled', 'Cancelled'), ('Approved', 'Approved'), ('Unapproved', 'Unapproved')]
    status = models.CharField(max_length=10, choices=statuses, default='Unapproved')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

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
        if not voucher.status == 'Approved':
            return
        entries = []
        for row in voucher.rows.all():
            amount = row.dr_amount if row.type == 'Dr' else row.cr_amount
            entries.append([row.type.lower(), row.account, amount])
        set_ledger_transactions(voucher, voucher.date, *entries)
        return


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
