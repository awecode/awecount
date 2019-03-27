from datetime import date

from django.db import models
from django.utils import timezone
from num2words import num2words

from apps.ledger.models import Party, Account, set_transactions as set_ledger_transactions, get_account
from apps.product.models import Item
from apps.tax.models import TaxScheme
from apps.users.models import Company, User
from awecount.utils import get_next_voucher_no, wGenerator
from awecount.utils.nepdate import ad2bs, string_from_tuple

STATUSES = (
    ('Draft', 'Draft'),
    ('Issued', 'Issued'),
    ('Cancelled', 'Cancelled'),
    ('Paid', 'Paid'),
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


class BankAccount(models.Model):
    account_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    branch_name = models.CharField(max_length=250, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_accounts')

    def __str__(self):
        return self.account_name + ': ' + self.company.name


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

    @staticmethod
    def apply_transactions(voucher):
        try:
            discount_expense = Account.objects.get(name='Discount Expenses', company=voucher.company,
                                                   category__name='Indirect Expenses')
        except Account.DoesNotExist:
            discount_expense = None

        if voucher.mode == 'Credit':
            # dr_acc = voucher.party.customer_account
            dr_acc = voucher.party.account
        else:
            cash_account = get_account(voucher.company, 'Cash')
            dr_acc = cash_account

        dividend_discount = 0

        if voucher.discount > 0 and voucher.discount_type:
            dividend_discount = voucher.discount_amount

        for row in voucher.rows.all():
            pure_total = row.quantity * row.rate
            # entries = [['cr', row.item.sale_ledger, pure_total]]
            entries = [['cr', row.item.ledger, pure_total]]

            if row.tax_scheme:
                entries.append(['cr', row.tax_scheme.payable, row.tax_amount])

            row_discount = 0

            if dividend_discount > 0:
                row_discount = (row.total / voucher.get_sub_total()) * dividend_discount

            if row.discount > 0:
                row_discount += row.discount_amount

            if row_discount > 0:
                entries.append(['dr', row.item.discount_ledger, row_discount])
            # elif discount_expense:
            #     entries.append(['dr', discount_expense, 0])

            entries.append(['dr', dr_acc, row.total])

            set_ledger_transactions(row, voucher.transaction_date, *entries)
        return


class SalesVoucherRow(models.Model):
    voucher = models.ForeignKey(SalesVoucher, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='sales_rows')

    def __str__(self):
        return str(self.voucher.voucher_no)

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
    receipt = models.FloatField()
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


class BankBranch(models.Model):
    location = models.CharField(max_length=255)
    bank = models.ForeignKey(Bank, related_name='branches', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    @property
    def name(self):
        bank_name = self.bank.short_name or self.bank.name
        _name = '{} {}'.format(bank_name, self.location)
        return _name

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
