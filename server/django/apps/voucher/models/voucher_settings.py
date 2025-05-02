from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.dispatch import receiver

from apps.bank.models import BankAccount
from apps.company.models import Company
from apps.product.models import InventorySetting
from apps.company.signals import company_created
from apps.voucher.models import PaymentMode

class SalesSetting(models.Model):
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="sales_setting"
    )

    show_party_by_default = models.BooleanField(default=True)

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    is_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)
    is_trade_discount_in_row = models.BooleanField(default=False)
    enable_due_date_in_voucher = models.BooleanField(default=False)

    # Required fields settings
    require_item_code = models.BooleanField(default=False)
    require_item_hs_code = models.BooleanField(default=False)

    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )
    mode = models.CharField(default="Credit", max_length=15)
    payment_mode = models.ForeignKey(
        "voucher.PaymentMode",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_setting",
    )
    enable_row_description = models.BooleanField(default=False)

    enable_import_challan = models.BooleanField(default=False)
    enable_amount_entry = models.BooleanField(default=False)
    show_rate_quantity_in_voucher = models.BooleanField(default=True)
    invoice_footer_text = models.TextField(null=True, blank=True)
    persist_pos_items = models.BooleanField(default=False)
    enable_sales_date_edit = models.BooleanField(default=False)
    default_email_attachments = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    @property
    def fields(self):
        return {
            "mode": self.bank_account_id or self.mode,
            "payment_mode": self.payment_mode_id,
            "trade_discount": self.is_trade_discount_in_voucher,
            "require_item_code": self.require_item_code,
            "require_item_hs_code": self.require_item_hs_code,
        }

    @property
    def options(self):
        return {
            "show_customer": not self.show_party_by_default,
            "show_trade_discount_in_voucher": self.show_trade_discount_in_voucher,
            "show_trade_discount_in_row": self.show_trade_discount_in_row,
            "enable_row_description": self.enable_row_description,
            "is_trade_discount_in_row": self.is_trade_discount_in_row,
            "enable_due_date_in_voucher": self.enable_due_date_in_voucher,
            "enable_import_challan": self.enable_import_challan,
            "enable_amount_entry": self.enable_amount_entry,
            "show_rate_quantity_in_voucher": self.show_rate_quantity_in_voucher,
            "persist_pos_items": self.persist_pos_items,
            "enable_sales_date_edit": self.enable_sales_date_edit,
            "require_item_code": self.require_item_code,
            "require_item_hs_code": self.require_item_hs_code,
        }

    def __str__(self):
        return "Sales Setting - {}".format(self.company.name)


class PurchaseSetting(models.Model):
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="purchase_setting"
    )

    show_trade_discount_in_voucher = models.BooleanField(default=False)
    is_trade_discount_in_voucher = models.BooleanField(default=False)
    show_trade_discount_in_row = models.BooleanField(default=False)
    is_trade_discount_in_row = models.BooleanField(default=False)
    enable_due_date_in_voucher = models.BooleanField(default=False)
    enable_empty_voucher_no = models.BooleanField(default=False)

    # Required fields settings
    require_item_code = models.BooleanField(default=False)
    require_item_hs_code = models.BooleanField(default=False)

    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )
    mode = models.CharField(default="Credit", max_length=15)
    payment_mode = models.ForeignKey(
        "voucher.PaymentMode",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_setting",
    )

    enable_row_description = models.BooleanField(default=False)
    enable_purchase_order_import = models.BooleanField(default=False)

    enable_item_rate_change_alert = models.BooleanField(default=False)
    rate_change_alert_emails = ArrayField(models.EmailField(), default=list, blank=True)

    def update(self, update_data):
        for key, value in update_data.items():
            if key == "bank_account":
                if update_data["bank_account"] == self.bank_account_id:
                    pass
                else:
                    self.bank_account_id = BankAccount.objects.get(
                        id=update_data["bank_account"]
                    ).id
            elif key == "payment_mode":
                self.payment_mode_id = PaymentMode.objects.get(
                    id=update_data["payment_mode"]
                ).id
            else:
                setattr(self, key, value)
        self.save()

    @property
    def fields(self):
        return {
            "mode": self.bank_account_id or self.mode,
            "payment_mode": self.payment_mode_id,
            "trade_discount": self.is_trade_discount_in_voucher,
            "require_item_code": self.require_item_code,
            "require_item_hs_code": self.require_item_hs_code,
        }

    @property
    def options(self):
        return {
            "show_trade_discount_in_voucher": self.show_trade_discount_in_voucher,
            "show_trade_discount_in_row": self.show_trade_discount_in_row,
            "enable_row_description": self.enable_row_description,
            "is_trade_discount_in_row": self.is_trade_discount_in_row,
            "enable_due_date_in_voucher": self.enable_due_date_in_voucher,
            "enable_purchase_order_import": self.enable_purchase_order_import,
            "require_item_code": self.require_item_code,
            "require_item_hs_code": self.require_item_hs_code,
        }

    def __str__(self):
        return "Purchase Setting - {}".format(self.company.name)


@receiver(company_created)
def handle_company_creation(sender, **kwargs):
    company = kwargs.get("company")
    SalesSetting.objects.create(company=company)
    PurchaseSetting.objects.create(company=company)
    InventorySetting.objects.create(company=company)
