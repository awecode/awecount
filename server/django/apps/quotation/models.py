from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.company.models import Company, CompanyBaseModel
from apps.ledger.models import (
    Party,
)
from apps.users.models import User
from apps.product.models import Item, Unit
from apps.tax.models import TaxScheme
from apps.voucher.models.agent import SalesAgent
from apps.voucher.models.discounts import SalesDiscount
from apps.quotation.base_models import QuotationRowModel

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
    reference = models.CharField(max_length=255, blank=True, null=True)
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

    @property
    def quotation_meta(self):
        return self.get_quotation_meta()

    def get_quotation_discount_data(self):
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            return {"type": discount_obj.type, "value": discount_obj.value}
        else:
            return {"type": self.discount_type, "value": self.discount}

    def get_quotation_meta(
        self, update_row_data=False, prefetched_rows=False, save=True
    ):
        dct = {
            "sub_total": 0,
            "sub_total_after_row_discounts": 0,
            "discount": 0,
            "non_taxable": 0,
            "taxable": 0,
            "tax": 0,
        }
        rows_data = []
        row_objs = {}
        # bypass prefetch cache using filter
        rows = self.rows.all() if prefetched_rows else self.rows.filter()
        for row in rows:
            row_data = dict(
                id=row.id,
                quantity=row.quantity,
                rate=row.rate,
                total=row.rate * row.quantity,
                row_discount=row.get_discount()[0] if row.has_discount() else 0,
            )
            row_data["gross_total"] = row_data["total"] - row_data["row_discount"]
            row_data["tax_rate"] = row.tax_scheme.rate if row.tax_scheme else 0
            dct["sub_total_after_row_discounts"] += row_data["gross_total"]
            dct["sub_total"] += row_data["total"]
            rows_data.append(row_data)
            row_objs[row.id] = row

        quotation_discount_data = self.get_quotation_discount_data()

        for row_data in rows_data:
            if quotation_discount_data["type"] == "Percent":
                dividend_discount = (
                    row_data["gross_total"] * quotation_discount_data["value"] / 100
                )
            elif quotation_discount_data["type"] == "Amount":
                dividend_discount = (
                    row_data["gross_total"]
                    * quotation_discount_data["value"]
                    / dct["sub_total_after_row_discounts"]
                )
            else:
                dividend_discount = 0
            row_data["dividend_discount"] = dividend_discount
            row_data["pure_total"] = row_data["gross_total"] - dividend_discount
            row_data["tax_amount"] = row_data["tax_rate"] * row_data["pure_total"] / 100
            total_row_discount = (
                row_data["row_discount"] + row_data["dividend_discount"]
            )
            dct["discount"] += total_row_discount
            dct["tax"] += row_data["tax_amount"]

            if row_data["tax_amount"]:
                dct["taxable"] += row_data["pure_total"]
            else:
                dct["non_taxable"] += row_data["pure_total"]

            if update_row_data:
                row_obj = row_objs[row_data["id"]]
                row_obj.discount_amount = total_row_discount
                row_obj.tax_amount = row_data["tax_amount"]
                row_obj.net_amount = row_data["pure_total"] + row_data["tax_amount"]
                row_obj.save()

        dct["grand_total"] = dct["sub_total"] - dct["discount"] + dct["tax"]

        for key, val in dct.items():
            dct[key] = round(val, 2)

        if save:
            self.meta_sub_total = dct["sub_total"]
            self.meta_sub_total_after_row_discounts = dct[
                "sub_total_after_row_discounts"
            ]
            self.meta_discount = dct["discount"]
            self.meta_non_taxable = dct["non_taxable"]
            self.meta_taxable = dct["taxable"]
            self.meta_tax = dct["tax"]
            self.save()

        return dct


class QuotationRow(QuotationRowModel, CompanyBaseModel):
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
