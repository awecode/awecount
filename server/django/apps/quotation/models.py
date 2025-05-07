from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.company.models import Company, CompanyBaseModel, FiscalYear
from apps.ledger.models import (
    Party,
)
from apps.users.models import User
from apps.product.models import Item, Unit
from apps.tax.models import TaxScheme
from apps.voucher.models.agent import SalesAgent
from apps.voucher.models.discounts import SalesDiscount

STATUSES = (
    ("Draft", "Draft"),
    ("Generated", "Generated"),
    ("Sent", "Sent"),
    ("Converted", "Converted"),
)

DISCOUNT_TYPES = (
    ("Amount", "Amount"),
    ("Percent", "Percent"),
)


class Quotation(CompanyBaseModel):
    number = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="quotations",
    )
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    generated_datetime = models.DateTimeField(blank=True, null=True)
    date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)

    discount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="quotations",
    )

    remarks = models.TextField(blank=True, null=True)
    is_export = models.BooleanField(default=False)

    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quotations")
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="quotations"
    )
    sales_agent = models.ForeignKey(
        SalesAgent,
        blank=True,
        null=True,
        related_name="quotations",
        on_delete=models.SET_NULL,
    )
    # Model key for module based permission
    key = "Quotations"

    class Meta:
        unique_together = ("company", "number")


class QuotationRow(CompanyBaseModel):
    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="quotation_rows"
    )
    description = models.TextField(blank=True, null=True)

    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("1.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="quotation_rows",
    )
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    discount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="quotation_rows",
    )
    tax_scheme = models.ForeignKey(
        TaxScheme,
        on_delete=models.CASCADE,
        related_name="quotation_rows",
        blank=True,
        null=True,
    )

    # Computed values
    discount_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    tax_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    net_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    # Model key for module based permission
    key = "Quotations"

    @property
    def amount_before_tax(self):
        return (self.net_amount or Decimal("0.0")) - (self.tax_amount or Decimal("0.0"))

    @property
    def amount_before_discount(self):
        return (
            (self.net_amount or Decimal("0.0"))
            - (self.tax_amount or Decimal("0.0"))
            + (self.discount_amount or Decimal("0.0"))
        )


class QuotationSetting(models.Model):
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="quotation_settings"
    )
    body_text = models.TextField(null=True, blank=True)
    footer_text = models.TextField(null=True, blank=True)

    @property
    def fields(self):
        return {
            "body_text": self.body_text,
            "footer_text": self.footer_text,
        }

    @property
    def options(self):
        return {
            "body_text": self.body_text,
            "footer_text": self.footer_text,
        }

    def __str__(self):
        return "Quotation Setting - {}".format(self.company.name)
