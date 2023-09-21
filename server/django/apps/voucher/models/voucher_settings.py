from django.db import models
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

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
    enable_due_date_in_voucher = models.BooleanField(default=False)

    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    mode = models.CharField(default='Credit', max_length=15)

    enable_row_description = models.BooleanField(default=False)

    enable_import_challan = models.BooleanField(default=False)
    enable_amount_entry = models.BooleanField(default=False)
    show_rate_quantity_in_voucher = models.BooleanField(default=True)
    invoice_footer_text = models.CharField(max_length=255, null=True, blank=True)

    @property
    def fields(self):
        return {
            'mode': self.bank_account_id or self.mode,
            'trade_discount': self.is_trade_discount_in_voucher
        }

    @property
    def options(self):
        return {
            'show_customer': not self.show_party_by_default,
            'show_trade_discount_in_voucher': self.show_trade_discount_in_voucher,
            'show_trade_discount_in_row': self.show_trade_discount_in_row,
            'enable_row_description': self.enable_row_description,
            'is_trade_discount_in_row': self.is_trade_discount_in_row,
            'enable_due_date_in_voucher': self.enable_due_date_in_voucher,
            'enable_import_challan': self.enable_import_challan,
            'enable_amount_entry': self.enable_amount_entry,
            'show_rate_quantity_in_voucher': self.show_rate_quantity_in_voucher
        }

    def __str__(self):
        return 'Sales Setting - {}'.format(self.company.name)


class PurchaseSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='purchase_setting')

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    is_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)
    is_trade_discount_in_row = models.BooleanField(default=False)
    enable_due_date_in_voucher = models.BooleanField(default=False)

    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.SET_NULL)
    mode = models.CharField(default='Credit', max_length=15)

    enable_row_description = models.BooleanField(default=False)
    enable_purchase_order_import = models.BooleanField(default=False)

    enable_item_rate_change_alert = models.BooleanField(default=False)
    rate_change_alert_emails = ArrayField(models.EmailField(), default=list, blank=True)

    def update(self, update_data):
        for key, value in update_data.items():
            if key == 'bank_account':
                if update_data['bank_account'] == self.bank_account_id:
                    pass
                else:
                    self.bank_account_id = BankAccount.objects.get(id=update_data['bank_account']).id
            else:
                setattr(self, key,value)
        self.save()

    @property
    def fields(self):
        return {
            'mode': self.bank_account_id or self.mode,
            'trade_discount': self.is_trade_discount_in_voucher
        }

    @property
    def options(self):
        return {
            'show_trade_discount_in_voucher': self.show_trade_discount_in_voucher,
            'show_trade_discount_in_row': self.show_trade_discount_in_row,
            'enable_row_description': self.enable_row_description,
            'is_trade_discount_in_row': self.is_trade_discount_in_row,
            'enable_due_date_in_voucher': self.enable_due_date_in_voucher,
            'enable_purchase_order_import': self.enable_purchase_order_import
        }

    def __str__(self):
        return 'Purchase Setting - {}'.format(self.company.name)
    

class InventorySetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='inventory_setting')

    enable_fifo = models.BooleanField(default=False)
    enable_negative_stock_check = models.BooleanField(default=False)

    def __str__(self) -> str:
        return 'Inventory Setting - {}'.format(self.company.name)


@receiver(company_creation)
def handle_company_creation(sender, **kwargs):
    company = kwargs.get('company')
    SalesSetting.objects.create(company=company)
    PurchaseSetting.objects.create(company=company)
    InventorySetting.objects.create(company=company)
