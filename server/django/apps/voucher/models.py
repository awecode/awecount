from auditlog.registry import auditlog
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.bank.models import BankAccount
from apps.ledger.models import Party, Account, set_transactions as set_ledger_transactions, get_account, JournalEntry, \
    TransactionModel
from apps.product.models import Item, Unit, JournalEntry as InventoryJournalEntry, set_inventory_transactions
from apps.tax.models import TaxScheme
from apps.users.models import Company, User, FiscalYear
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


class SalesVoucher(TransactionModel):
    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    issue_datetime = models.DateTimeField(default=timezone.now)
    transaction_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)

    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='sales')
    # total_amount = models.FloatField(null=True, blank=True)  #
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    epayment = models.CharField(max_length=50, blank=True, null=True)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    remarks = models.TextField(blank=True, null=True)
    is_export = models.BooleanField(default=False)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_vouchers')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_vouchers')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='sale_vouchers')

    class Meta:
        unique_together = ('company', 'voucher_no', 'fiscal_year')

    @property
    def buyer_name(self):
        if self.party:
            return self.party.name
        return self.customer_name

    def is_issued(self):
        return self.status != 'Draft'

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

    # @property
    # def total_amount(self):
    #     return self.get_sub_total() - self.get_discount()[0] + self.get_tax_amount()[1]

    @property
    def bs_date(self):
        return string_from_tuple(ad2bs(self.transaction_date.strftime('%Y-%m-%d')))

    # def get_tax_amount(self):
    #     tax_scheme = []
    #     tax_amount = 0
    #     for row in self.rows.all():
    #         if row.tax_scheme:
    #             tax_object = row.tax_scheme
    #             tax_scheme.append(tax_object.name)
    #             tax_amount = tax_amount + row.tax_amount
    #     tax_text = 'TAX'
    #     if tax_scheme and len(set(tax_scheme)) == 1:
    #         tax_text = tax_scheme[0]
    #     return tax_text, tax_amount

    def get_sub_total(self):
        total = 0
        for row in self.rows.all():
            total += row.total
        return total

    def get_row_discounts(self):
        total = 0
        for row in self.rows.all():
            total += row.get_discount()[0]
        return total

    def get_total_after_row_discounts(self):
        total = 0
        for row in self.rows.all():
            total += row.total_after_row_discount
        return total

    def get_discount(self, sub_total_after_row_discounts=None):
        """
        :type sub_total_after_row_discounts: float
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total_after_row_discounts = sub_total_after_row_discounts or self.get_total_after_row_discounts()
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total_after_row_discounts * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total_after_row_discounts * (self.discount / 100), False
        return 0, False

    def get_voucher_discount_data(self):
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            return {'type': discount_obj.type, 'value': discount_obj.value}
        else:
            return {'type': self.discount_type, 'value': self.discount}

    def get_voucher_meta(self):
        dct = {
            'sub_total': 0,
            'discount': 0,
            'tax': 0
        }
        rows_data = []
        # gross_total_sum is subtotal after row discounts, before voucher discount and tax
        gross_total_sum = 0
        for row in self.rows.all():
            row_data = {'quantity': row.quantity, 'rate': row.rate, 'total': row.rate * row.quantity}
            row_data['row_discount'] = row.get_discount()[0] if row.has_discount() else 0
            row_data['gross_total'] = row_data['total'] - row_data['row_discount']
            row_data['tax_rate'] = row.tax_scheme.rate if row.tax_scheme else 0
            gross_total_sum += row_data['gross_total']
            dct['sub_total'] += row_data['total']
            rows_data.append(row_data)

        voucher_discount_data = self.get_voucher_discount_data()

        for row_data in rows_data:
            if voucher_discount_data['type'] == 'Percent':
                dividend_discount = row_data['gross_total'] * voucher_discount_data['value'] / 100
            elif voucher_discount_data['type'] == 'Amount':
                dividend_discount = row_data['gross_total'] * voucher_discount_data['value'] / gross_total_sum
            else:
                dividend_discount = 0
            row_data['dividend_discount'] = dividend_discount
            row_data['pure_total'] = row_data['gross_total'] - dividend_discount
            row_data['tax_amount'] = row_data['tax_rate'] * row_data['pure_total'] / 100

            dct['discount'] += row_data['row_discount'] + row_data['dividend_discount']
            dct['tax'] += row_data['tax_amount']

        dct['grand_total'] = dct['sub_total'] - dct['discount'] + dct['tax']
        
        for key, val in dct.items():
            dct[key] = round(val, 2)

        return dct

    def apply_cancel_transaction(self):
        content_type = ContentType.objects.get(model='salesvoucherrow')
        row_ids = [row.id for row in self.rows.all()]
        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        InventoryJournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()

    def mark_as_paid(self):
        if self.mode == 'Credit' and self.status == 'Issued':
            self.status = 'Paid'
            # sale_voucher.apply_mark_as_paid()
            self.save()
        else:
            raise ValueError('This sales cannot be mark as paid!')

    def cancel(self):
        self.status = 'Cancelled'
        self.save()
        self.apply_cancel_transaction()

    # def apply_mark_as_paid(self):
    #     today = timezone.now().today()
    #     entries = []
    #     total = self.total_amount
    #     cash_account = get_account(self.company, 'Cash')
    #     entries.append(['cr', self.party.customer_account, total])
    #     entries.append(['dr', cash_account, total])
    #     set_ledger_transactions(self, today, *entries)

    @staticmethod
    def apply_transactions(voucher):
        # entries = []
        if voucher.status == 'Cancelled':
            voucher.apply_cancel_transaction()

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

        # sub_total = voucher.get_sub_total()
        sub_total_after_row_discounts = voucher.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = voucher.get_discount(sub_total_after_row_discounts)

        # filter bypasses rows cached by prefetching
        for row in voucher.rows.filter():
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

            set_ledger_transactions(row, voucher.transaction_date, *entries, clear=True)

        # Following set_ledger transactions stays outside for loop
        # set_ledger_transactions(voucher, voucher.transaction_date, *entries, clear=True)
        SalesVoucher.apply_inventory_transaction(voucher)

    @staticmethod
    def apply_inventory_transaction(voucher):
        # TO DO check for item type consumable and non consumable
        for row in voucher.rows.all():
            set_inventory_transactions(
                row,
                voucher.transaction_date,
                ['cr', row.item.account, int(row.quantity)],
            )

    def save(self, *args, **kwargs):
        if self.status not in ['Draft', 'Cancelled'] and not self.voucher_no:
            raise ValueError('Issued invoices need a voucher number!')
        super().save(*args, **kwargs)


class SalesVoucherRow(TransactionModel):
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

    def __str__(self):
        return str(self.voucher.voucher_no)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher_id

    def has_discount(self):
        return True if self.discount_obj_id or self.discount_type in ['Amount', 'Percent'] and self.discount else False

    def get_discount(self):
        """
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total = self.quantity * self.rate
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total * (self.discount / 100), False
        return 0, False

    def get_tax_amount(self):
        amount = 0
        if self.tax_scheme:
            amount = (self.tax_scheme.rate / 100) * self.total
        return amount

    @property
    def total(self):
        row_total = self.quantity * self.rate
        # sub_total = sub_total - self.get_discount()[0]
        return row_total

    @property
    def total_after_row_discount(self):
        row_total = self.quantity * self.rate
        row_total = row_total - self.get_discount()[0]
        return row_total


class PurchaseVoucher(TransactionModel):
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

    # tax_choices = [('No Tax', 'No Tax'), ('Tax Inclusive', 'Tax Inclusive'), ('Tax Exclusive', 'Tax Exclusive'), ]
    # tax = models.CharField(max_length=10, choices=tax_choices, default='inclusive', null=True, blank=True)
    # tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, on_delete=models.CASCADE)

    def type(self):
        return 'Credit' if self.credit else 'Cash'

    def apply_cancel_transaction(self):
        content_type = ContentType.objects.get(model='purchasesvoucherrow')
        row_ids = [row.id for row in self.rows.all()]
        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        InventoryJournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()

    @staticmethod
    def apply_inventory_transaction(voucher):
        for row in voucher.rows.all():
            set_inventory_transactions(
                row,
                voucher.date,
                ['dr', row.item.account, int(row.quantity)],
            )

    @property
    def voucher_type(self):
        return 'PurchaseVoucher'

    @property
    def total_amount(self):
        return self.get_sub_total() - self.get_discount()[0] + self.get_tax_amount()[1]

    def get_tax_amount(self):
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

    def get_total_after_row_discounts(self):
        total = 0
        for row in self.rows.all():
            total += row.total_after_row_discount
        return total

    def get_discount(self, sub_total_after_row_discounts=None):
        """
        :type sub_total_after_row_discounts: float
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total_after_row_discounts = sub_total_after_row_discounts or self.get_total_after_row_discounts()
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total_after_row_discounts * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total_after_row_discounts * (self.discount / 100), False
        return 0, False

    @staticmethod
    def apply_transactions(voucher):
        # if voucher.status == 'Cancelled':
        #     voucher.apply_cancel_transaction()
        # entries = []
        if voucher.status == 'Cancelled':
            voucher.apply_cancel_transaction()
        if not voucher.status == 'Issued':
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if voucher.mode == 'Credit':
            cr_acc = voucher.party.customer_account
        elif voucher.mode == 'Cash':
            cr_acc = get_account(voucher.company, 'Cash')
            voucher.status = 'Paid'
        # TODO Allow creating cheque deposit
        elif voucher.mode == 'Cheque':
            cr_acc = voucher.party.customer_account
            voucher.status = 'Paid'
        elif voucher.mode == 'Bank Deposit':
            cr_acc = voucher.bank_account.ledger
            voucher.status = 'Paid'
        # elif voucher.mode == 'ePayment':
        #     pass

        voucher.save()

        # sub_total = voucher.get_sub_total()
        sub_total_after_row_discounts = voucher.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = voucher.get_discount(sub_total_after_row_discounts)

        for row in voucher.rows.all():
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
                entries.append(['cr', row.item.discount_allowed_ledger, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['dr', row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['dr', row.item.purchase_ledger, purchase_value])
            entries.append(['cr', cr_acc, row_total])
            set_ledger_transactions(row, voucher.date, *entries, clear=True)

        PurchaseVoucher.apply_inventory_transaction(voucher)

    @property
    def row_discount_total(self):
        grand_total = 0
        # for obj in self.rows.all():
        #     total = obj.quantity * obj.rate
        #     discount = get_discount_with_percent(total, obj.discount)
        #     grand_total += discount
        return grand_total


class PurchaseVoucherRow(TransactionModel):
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
        self.item.cost_price = self.rate
        self.item.save()
        super(PurchaseVoucherRow, self).save(*args, **kwargs)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher_id

    def has_discount(self):
        return True if self.discount_obj_id or (
            self.discount_type in ['Amount', 'Percent'] and self.discount) else False

    def get_discount(self):
        """
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total = self.quantity * self.rate
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total * (self.discount / 100), False
        return 0, False

    # @property
    # def tax_amount(self):
    #     amount = 0
    #     if self.tax_scheme:
    #         amount = (self.tax_scheme.rate / 100) * self.total
    #     return amount

    @property
    def total(self):
        row_total = self.quantity * self.rate
        # sub_total = sub_total - self.get_discount()[0]
        return row_total

    @property
    def total_after_row_discount(self):
        row_total = self.quantity * self.rate
        row_total = row_total - self.get_discount()[0]
        return row_total


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

    class Meta:
        unique_together = ('company', 'voucher_no')

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
        row_ids = [row.id for row in self.rows.all()]
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
