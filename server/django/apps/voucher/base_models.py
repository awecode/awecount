from datetime import datetime
from decimal import Decimal

import requests
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models

from apps.ledger.models import JournalEntry
from awecount.libs import nepdate, wGenerator


class InvoiceModel(models.Model):
    meta_sub_total = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    meta_sub_total_after_row_discounts = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    meta_discount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    meta_non_taxable = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    meta_taxable = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    meta_tax = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    def __str__(self):
        return str(self.voucher_no)

    @property
    def voucher_type(self):
        return self.__class__.__name__

    def is_issued(self):
        return self.status != "Draft"

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.get_voucher_meta()["grand_total"])

    def get_total_after_row_discounts(self, use_prefetched=False):
        total = 0
        rows = self.rows.all() if use_prefetched else self.rows.filter()
        for row in rows:
            total += row.total_after_row_discount
        return total

    def get_discount(self, sub_total_after_row_discounts=None, use_prefetched=False):
        """
        :param use_prefetched: controls if prefetched rows are to be used
        :type sub_total_after_row_discounts: float or None
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        # Allow 0
        if sub_total_after_row_discounts is None:
            sub_total_after_row_discounts = self.get_total_after_row_discounts(
                use_prefetched=use_prefetched
            )
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == "Amount":
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == "Percent":
                return sub_total_after_row_discounts * (
                    discount_obj.value / 100
                ), discount_obj.trade_discount
        elif self.discount and self.discount_type == "Amount":
            return self.discount, self.trade_discount
        elif self.discount and self.discount_type == "Percent":
            return sub_total_after_row_discounts * (
                self.discount / 100
            ), self.trade_discount
        return 0, False

    # Used by generate_meta
    def get_voucher_discount_data(self):
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            return {"type": discount_obj.type, "value": discount_obj.value}
        else:
            return {"type": self.discount_type, "value": self.discount}

    @property
    def voucher_meta(self):
        return self.get_voucher_meta()

    def generate_meta(self, update_row_data=False, prefetched_rows=False, save=True):
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

        voucher_discount_data = self.get_voucher_discount_data()

        for row_data in rows_data:
            if voucher_discount_data["type"] == "Percent":
                dividend_discount = (
                    row_data["gross_total"] * voucher_discount_data["value"] / 100
                )
            elif voucher_discount_data["type"] == "Amount":
                dividend_discount = (
                    row_data["gross_total"]
                    * voucher_discount_data["value"]
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

    def get_voucher_meta(self, update_row_data=False, prefetched_rows=False):
        if self.meta_tax is None:
            self.generate_meta(save=True)
        dct = {
            "sub_total": self.meta_sub_total,
            "sub_total_after_row_discounts": self.meta_sub_total_after_row_discounts,
            "discount": self.meta_discount,
            "non_taxable": self.meta_non_taxable,
            "taxable": self.meta_taxable,
            "tax": self.meta_tax,
        }
        dct["grand_total"] = dct["sub_total"] - dct["discount"] + dct["tax"]
        return dct

    def cancel(self, message=None):
        self.status = "Cancelled"
        if message:
            self.remarks = self.remarks or ""
            self.remarks += "\nReason for cancellation: " + message
        self.save()
        self.cancel_transactions()

    def cancel_transactions(self):
        InventoryJournalEntry = apps.get_model("product", "JournalEntry")

        content_type = ContentType.objects.get(
            model=self.__class__.__name__.lower() + "row"
        )
        row_ids = self.rows.values_list("id", flat=True)
        JournalEntry.objects.filter(
            content_type=content_type, object_id__in=row_ids
        ).delete()
        InventoryJournalEntry.objects.filter(
            content_type=content_type, object_id__in=row_ids
        ).delete()

    def mark_as_resolved(self, status="Resolved"):
        if self.mode == "Credit" and self.status in ["Issued", "Partially Paid"]:
            self.status = status
            self.save()
        else:
            raise ValueError("This voucher cannot be mark as resolved!")

    def party_tax_reg_no(self):
        if self.party_id and self.party.tax_identification_number:
            return self.party.tax_identification_number
        return ""

    def party_name(self):
        if self.party_id and self.party.name:
            return self.party.name
        if hasattr(self, "customer_name") and self.customer_name:
            return self.customer_name
        return ""

    def synchronize(self):
        if (
            self.company.synchronize_cbms_nepal_live
            or self.company.synchronize_cbms_nepal_test
        ):
            if self.company.synchronize_cbms_nepal_test:
                conf = settings.CBMS_NEPAL.get("TEST")
            else:
                conf = settings.CBMS_NEPAL.get("LIVE")
            data, endpoint = self.cbms_nepal_data(conf)
            data["username"] = conf["username"]
            data["password"] = conf["password"]
            data["isrealtime"] = True
            data["datetimeclient"] = datetime.now().strftime("%-m/%-d/%Y %H:%M:%S %p")
            data["fiscal_year"] = nepdate.get_fiscal_year_for_cbms()
            response = requests.post(url=conf["base_url"] + endpoint, data=data)
            print(response.text)

    class Meta:
        abstract = True


class InvoiceRowModel(models.Model):
    company_id_accessor = "voucher__company_id"

    def __str__(self):
        return str(self.voucher.voucher_no)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher_id

    def has_discount(self):
        return (
            True
            if self.discount_obj_id
            or self.discount_type in ["Amount", "Percent"]
            and self.discount
            else False
        )

    def get_discount(self):
        """
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total = self.quantity * self.rate
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == "Amount":
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == "Percent":
                return sub_total * (
                    discount_obj.value / 100
                ), discount_obj.trade_discount
        elif self.discount and self.discount_type == "Amount":
            return self.discount, self.trade_discount
        elif self.discount and self.discount_type == "Percent":
            return sub_total * (self.discount / 100), self.trade_discount
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

    class Meta:
        abstract = True
