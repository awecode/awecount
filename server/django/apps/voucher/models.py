from datetime import date

from django.db import models
from django.utils import timezone

from apps.ledger.models import Party, Account, set_transactions as set_ledger_transactions
from apps.product.models import Item
from apps.tax.models import TaxScheme
from apps.users.models import Company, User
from awecount.utils import get_next_voucher_no

STATUSES = (
    ('Draft', 'Draft'),
    ('Issued', 'Issued'),
    ('Cancelled', 'Cancelled'),
    ('Paid', 'Paid'),
)

MODES = (
    ('Party', 'Party'),
    ('Cash', 'Cash'),
    ('eSewa', 'eSewa'),
    ('Khalti', 'Khalti'),
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

    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_vouchers')

    def __str__(self):
        return str(self.voucher_no)

    @property
    def discount_amount(self):
        discount = 0
        if self.discount and self.discount_type == 'Amount':
            discount = self.discount
        elif self.discount and self.discount_type == 'Percent':
            discount = self.total_amount * (self.discount / 100)
        return discount

    @staticmethod
    def apply_transactions(voucher):
        entries = []
        discount_expense = Account.objects.get(name='Discount Expenses', company=voucher.company,
                                               category__name='Indirect Expenses')

        # TODO Voucher discount needs to broken into row discounts
        # if voucher.discount and voucher.discount_expense:
        #     set_ledger_transactions(voucher, voucher.transaction_date, ['dr', discount_expense, voucher.discount_amount])

        # TODO create party supplier and customer account
        # dr_acc = voucher.party.customer_account
        for row in voucher.rows.all():
            tax_amt = 0
            total = row.quantity * row.rate

            # TODO If the voucher has discount, apply discount proportionally
            # if discount_rate:
            #     if obj.tax == 'inclusive' and tax_scheme:
            #         discount_rate = discount_rate * 100 / (100 + tax_scheme.percent)
            #     divident_discount = (pure_total - row_discount) * discount_rate

            entries.append(['cr', row.item.ledger, total])

            if row.tax_scheme:
                tax_amt = (total) * row.tax_scheme.rate / 100
                entries.append(['cr', row.tax_scheme.payable, tax_amt])

            if row.discount and row.discount_expense:
                entries.append(['dr', discount_expense, row.discount_amount])

            # TODO receivalble account create in party
            receivable = total - row.discount_amount + tax_amt
            # entries.append(['dr', dr_acc, receivable])

            set_ledger_transactions(row, voucher.transaction_date, *entries)
        return


class SalesVoucherRow(models.Model):
    voucher = models.ForeignKey(SalesVoucher, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
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
    invoice = models.ForeignKey(SalesVoucher, related_name='receipts', on_delete=models.CASCADE)
    receipt = models.FloatField()
    discount = models.FloatField(blank=True, null=True)
    cash_receipt = models.ForeignKey(CreditVoucher, related_name='rows', on_delete=models.CASCADE)

    def get_voucher_no(self):
        return self.cash_receipt.voucher_no

    def get_absolute_url(self):
        return 'url'
        # return reverse_lazy('credit_voucher_edit', kwargs={'pk': self.cash_receipt_id})

    def overdue_days(self):
        if self.invoice.due_date and self.invoice.due_date < date.today():
            overdue_days = date.today() - self.invoice.due_date
            return overdue_days.days
        return ''

    class Meta:
        unique_together = ('invoice', 'cash_receipt')


class Bank(models.Model):
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=50)


class BankBranch(models.Model):
    location = models.CharField(max_length=255)
    bank = models.ForeignKey(Bank, related_name='branches', on_delete=models.CASCADE)

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

    def __str__(self):
        return self.date.strftime('%d-%m-%Y') + '- ' + self.user.full_name
