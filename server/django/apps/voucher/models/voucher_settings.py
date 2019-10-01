from django.db import models
from django.dispatch import receiver

from apps.bank.models import BankAccount
from apps.users.models import Company
from apps.users.signals import company_creation


class SalesSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='sales_setting')

    show_party_by_default = models.BooleanField(default=True)

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    is_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)
    is_trade_discount_in_row = models.BooleanField(default=False)

    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    mode = models.CharField(default='Credit', max_length=15)

    enable_row_description = models.BooleanField(default=False)

    def __str__(self):
        return 'Sales Setting - {}'.format(self.company.name)


class PurchaseSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='purchase_setting')

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    is_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)
    is_trade_discount_in_row = models.BooleanField(default=False)

    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    mode = models.CharField(default='Credit', max_length=15)

    enable_row_description = models.BooleanField(default=False)

    def __str__(self):
        return 'Purchase Setting - {}'.format(self.company.name)


@receiver(company_creation)
def handle_company_creation(sender, **kwargs):
    company = kwargs.get('company')
    SalesSetting.objects.create(company=company)
    PurchaseSetting.objects.create(company=company)
