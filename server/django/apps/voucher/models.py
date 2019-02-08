from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.ledger.models import Party
from apps.users.models import Company

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


class SalesVoucher(models.Model):
    voucher_no = models.PositiveSmallIntegerField()
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    issue_datetime = models.DateTimeField(default=timezone.now)
    transaction_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_vouchers')
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0])
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_vouchers')
    remarks = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    discount = models.FloatField(default=0)
    total_amount = models.FloatField(null=True, blank=True)
    mode = models.CharField(choices=STATUSES, default=MODES[0][0])


class SalesVoucherRow(models.Model):
    pass