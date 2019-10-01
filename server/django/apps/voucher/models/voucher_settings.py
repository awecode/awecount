from django.db import models

from apps.bank.models import BankAccount
from apps.users.models import Company


class SalesSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='sales_setting')

    show_party_by_default = models.BooleanField(default=True)

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)

    mode = models.CharField(default='Credit', max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    enable_row_description = models.BooleanField(default=False)


class PurchaseSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='purchase_setting')

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)

    mode = models.CharField(default='Credit', max_length=15)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)

    enable_row_description = models.BooleanField(default=False)
