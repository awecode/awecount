from django.db import models
from django.utils import timezone

from apps.ledger.models import Party
from apps.product.models import Item
from apps.tax.models import TaxScheme
from apps.users.models import Company, User

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
    def total(self):
        sub_total = self.quantity * self.rate
        if self.discount and self.discount_type:
            if self.discount_type == 'Amount':
                sub_total = sub_total - self.discount
            elif self.discount_type == 'Percent':
                sub_total = sub_total - (sub_total * (self.discount / 100))
        return sub_total
