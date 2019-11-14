from auditlog.registry import auditlog
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from apps.bank.models import BankAccount, ChequeDeposit
from apps.ledger.models import Party, set_transactions as set_ledger_transactions, get_account, TransactionModel, \
    TransactionCharge
from apps.product.models import Item, Unit, set_inventory_transactions
from apps.tax.models import TaxScheme
from apps.users.models import Company, User, FiscalYear
from apps.voucher.base_models import InvoiceModel, InvoiceRowModel
from awecount.utils import nepdate
from awecount.utils.helpers import merge_dicts

from .discounts import DISCOUNT_TYPES, PurchaseDiscount, SalesDiscount
from .invoice_design import InvoiceDesign
from .journal_vouchers import JournalVoucher, JournalVoucherRow
from .agent import SalesAgent
from .voucher_settings import SalesSetting, PurchaseSetting

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
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='sales')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    remarks = models.TextField(blank=True, null=True)
    is_export = models.BooleanField(default=False)

    total_amount = models.FloatField(blank=True, null=True)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_invoices')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_invoices')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='sales_invoices')
    sales_agent = models.ForeignKey(SalesAgent, blank=True, null=True, related_name='sales_invoices',
                                    on_delete=models.SET_NULL)

    # Model key for module based permission
    key = 'Sales'

    class Meta:
        unique_together = ('company', 'voucher_no', 'fiscal_year')

    @property
    def buyer_name(self):
        if self.party_id:
            return self.party.name
        return self.customer_name

    def apply_inventory_transactions(self):
        for row in self.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related(
                'item__account'):
            set_inventory_transactions(
                row,
                self.date,
                ['cr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self, voucher_meta=None):

        voucher_meta = voucher_meta or self.get_voucher_meta()
        if self.total_amount != voucher_meta['grand_total']:
            self.total_amount = voucher_meta['grand_total']
            self.save()

        if self.status == 'Cancelled':
            self.cancel_transactions()
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
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_allowed_account',
                                                     'item__sales_account'):
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
                entries.append(['dr', row.item.discount_allowed_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['cr', row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['cr', row.item.sales_account, sales_value])
            entries.append(['dr', dr_acc, row_total])

            set_ledger_transactions(row, self.date, *entries, clear=True)
        self.apply_inventory_transactions()

    def save(self, *args, **kwargs):
        if self.status not in ['Draft', 'Cancelled'] and not self.voucher_no:
            raise ValueError('Issued invoices need a voucher number!')
        super().save(*args, **kwargs)

    def cbms_nepal_data(self, conf):
        meta = self.get_voucher_meta()
        data = {
            'seller_pan': self.company.tax_registration_number,
            'buyer_pan': self.party_tax_reg_no(),
            'buyer_name': self.party_name(),
            'total_sales': meta['grand_total'],
            'taxable_sales_vat': meta['taxable'],
            'vat': meta['tax'],
            'export_sales': 0,
            'tax_exempted_sales': meta['non_taxable'],
            'invoice_number': self.voucher_no,
            'invoice_date': nepdate.string_from_tuple(nepdate.ad2bs(str(self.date))).replace('-', '.')
        }
        if self.is_export:
            data['taxable_sales_vat'] = 0
            data['vat'] = 0
            data['export_sales'] = meta['grand_total']
            data['tax_exempted_sales'] = meta['grand_total']

        merged_data = dict(merge_dicts(data, conf['data']))
        merged_data = dict(merge_dicts(merged_data, conf['sales_invoice_data']))
        return merged_data, conf['sales_invoice_endpoint']

    @property
    def pdf_url(self):
        return '{}sales-voucher/{}/view?pdf=1'.format(settings.BASE_URL, self.pk)

    @property
    def view_url(self):
        return '{}sales-voucher/{}/view'.format(settings.BASE_URL, self.pk)


class SalesVoucherRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(SalesVoucher, on_delete=models.CASCADE, related_name='rows')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sales_rows')
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='sales_rows')
    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='sales_rows')

    # Computed values
    discount_amount = models.FloatField(blank=True, null=True)
    tax_amount = models.FloatField(blank=True, null=True)
    net_amount = models.FloatField(blank=True, null=True)

    # Model key for module based permission
    key = 'Sales'


class PurchaseVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.CharField(max_length=25)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    discount = models.FloatField(default=0)
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True)
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='purchases')

    remarks = models.TextField(blank=True, null=True)
    is_import = models.BooleanField(default=False)

    total_amount = models.FloatField(blank=True, null=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_vouchers')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='purchase_vouchers')

    @property
    def buyer_name(self):
        if self.party_id:
            return self.party.name

    def apply_inventory_transaction(self):
        for row in self.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related(
                'item__account'):
            set_inventory_transactions(
                row,
                self.date,
                ['dr', row.item.account, int(row.quantity)],
            )

    def apply_transactions(self):

        voucher_meta = self.get_voucher_meta()
        if self.total_amount != voucher_meta['grand_total']:
            self.total_amount = voucher_meta['grand_total']
            self.save()

        if self.status == 'Cancelled':
            self.cancel_transactions()
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
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_received_account',
                                                     'item__purchase_account'):
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

            item = row.item
            if row_discount > 0:
                entries.append(['cr', item.discount_received_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['dr', row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['dr', item.dr_account, purchase_value])

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
    trade_discount = models.BooleanField(default=False)
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
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(SalesDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='credit_notes')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    total_amount = models.FloatField(blank=True, null=True)

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
        voucher_meta = self.get_voucher_meta()
        if self.total_amount != voucher_meta['grand_total']:
            self.total_amount = voucher_meta['grand_total']
            self.save()

        if self.status == 'Cancelled':
            self.cancel_transactions()
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
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_allowed_account',
                                                     'item__sales_account'):
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
                entries.append(['cr', row.item.discount_allowed_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['dr', row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['dr', row.item.sales_account, sales_value])
            entries.append(['cr', cr_acc, row_total])

            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()

    def cbms_nepal_data(self, conf):
        invoice = self.invoices.first()
        if invoice:
            meta = invoice.get_voucher_meta()
            data = {
                'seller_pan': self.company.tax_registration_number,
                'buyer_pan': self.party_tax_reg_no(),
                'buyer_name': self.party_name(),
                'total_sales': meta['grand_total'],
                'taxable_sales_vat': meta['taxable'],
                'vat': meta['tax'],
                'export_sales': 0,
                'tax_exempted_sales': meta['non_taxable'],
                'ref_invoice_number': invoice.voucher_no,
                'credit_note_number': self.voucher_no,
                'credit_note_date': nepdate.string_from_tuple(nepdate.ad2bs(str(self.date))).replace('-', '.'),
                'reason_for_return': self.remarks,
            }
            if invoice.is_export:
                data['taxable_sales_vat'] = 0
                data['vat'] = 0
                data['export_sales'] = meta['grand_total']
                data['tax_exempted_sales'] = meta['grand_total']

            merged_data = dict(merge_dicts(data, conf['data']))
            merged_data = dict(merge_dicts(merged_data, conf['credit_note_data']))
            return merged_data, conf['credit_note_endpoint']


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
    trade_discount = models.BooleanField(default=False)
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
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='debit_notes')
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    total_amount = models.FloatField(blank=True, null=True)

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
        voucher_meta = self.get_voucher_meta()
        if self.total_amount != voucher_meta['grand_total']:
            self.total_amount = voucher_meta['grand_total']
            self.save()

        if self.status == 'Cancelled':
            self.cancel_transactions()
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
        for row in self.rows.filter().select_related('tax_scheme', 'discount_obj', 'item__discount_received_account',
                                                     'item__purchase_account'):
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

            item = row.item
            if row_discount > 0:
                entries.append(['dr', item.discount_received_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(['cr', row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(['cr', item.dr_account, purchase_value])

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
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(PurchaseDiscount, blank=True, null=True, on_delete=models.SET_NULL,
                                     related_name='debit_note_rows')

    tax_scheme = models.ForeignKey(TaxScheme, on_delete=models.CASCADE, related_name='debit_note_rows')


PAYMENT_MODES = (
    ('Cheque', 'Cheque'),
    ('Cash', 'Cash'),
    ('Bank Deposit', 'Bank Deposit'),
)


class PaymentReceipt(models.Model):
    invoices = models.ManyToManyField(SalesVoucher, related_name='payment_receipts')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='payment_receipts')
    date = models.DateField()
    mode = models.CharField(choices=PAYMENT_MODES, default=PAYMENT_MODES[0][0], max_length=15)
    transaction_charge_account = models.ForeignKey(TransactionCharge, related_name='payment_receipts', blank=True, null=True, on_delete=models.PROTECT)
    transaction_charge = models.FloatField(default=0)
    bank_account = models.ForeignKey(BankAccount, related_name='payment_receipts', on_delete=models.CASCADE, blank=True,
                                     null=True)
    cheque_deposit = models.ForeignKey(ChequeDeposit, blank=True, null=True, related_name='payment_receipts',
                                       on_delete=models.SET_NULL)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.date)


auditlog.register(SalesVoucher)
auditlog.register(SalesVoucherRow)
auditlog.register(PurchaseVoucher)
auditlog.register(PurchaseVoucherRow)
auditlog.register(CreditNote)
auditlog.register(CreditNoteRow)
auditlog.register(DebitNote)
auditlog.register(DebitNoteRow)
