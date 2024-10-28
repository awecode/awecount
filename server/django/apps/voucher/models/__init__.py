import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from auditlog.registry import auditlog
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch, Q
from django.utils import timezone

from apps.bank.models import BankAccount, ChequeDeposit
from apps.ledger.models import (
    JournalEntry,
    Party,
    Transaction,
    TransactionCharge,
    TransactionModel,
    get_account,
)
from apps.ledger.models import set_transactions as set_ledger_transactions
from apps.product.models import (
    Item,
    Unit,
    find_obsolete_transactions,
    set_inventory_transactions,
)
from apps.tax.models import TaxScheme
from apps.users.models import Company, FiscalYear, User
from apps.voucher.base_models import InvoiceModel, InvoiceRowModel
from awecount.libs import decimalize, nepdate
from awecount.libs.helpers import merge_dicts

from .agent import SalesAgent
from .discounts import DISCOUNT_TYPES, PurchaseDiscount, SalesDiscount

STATUSES = (
    ("Draft", "Draft"),
    ("Issued", "Issued"),
    ("Cancelled", "Cancelled"),
    ("Paid", "Paid"),
    ("Partially Paid", "Partially Paid"),
)

CHALLAN_STATUSES = (
    ("Draft", "Draft"),
    ("Issued", "Issued"),
    ("Cancelled", "Cancelled"),
    ("Resolved", "Resolved"),
    # ('Approved', 'Approved'),
    # ('Unapproved', 'Unapproved'),
)

PURCHASE_ORDER_STATUS_CHOICES = [
    # ('Draft', 'Draft'),
    ("Issued", "Issued"),
    # ('Resolved', 'Resolved'),
    ("Cancelled", "Cancelled"),
]

MODES = (
    ("Credit", "Credit"),
    ("Cash", "Cash"),
    ("Bank Deposit", "Bank Deposit"),
)

ADJUSTMENT_STATUS_CHOICES = (("Issued", "Issued"), ("Cancelled", "Cancelled"))
PURPOSE_CHOICES = (
    ("Stock In", "Stock In"),
    ("Stock Out", "Stock Out"),
    ("Damaged", "Damaged"),
    ("Expired", "Expired"),
)
CONVERSION_CHOICES = (("Issued", "Issued"), ("Cancelled", "Cancelled"))
TRANSACTION_TYPE_CHOICES = [
    ("Cr", "Cr"),
    ("Dr", "Dr"),
]


class FeeType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    SLAB_BASED = "slab_based"
    SLIDING_SCALE = "sliding_scale"
    TIME_BASED = "time_based"  # Not implemented yet


class TransactionFeeConfig:
    def __init__(self, fee_config: dict):
        self.fee_config = fee_config
        self.validate()

    def _validate_slabs(self):
        slabs = self.fee_config["slabs"]
        if not isinstance(slabs, list):
            raise ValueError("Slabs must be a list")

        prev_max = Decimal("0")
        for slab in slabs:
            if not all(key in slab for key in ["min_amount", "rate"]):
                raise ValueError("Each slab must specify min_amount and rate")

            current_min = Decimal(str(slab["min_amount"]))
            if current_min != prev_max:
                raise ValueError("Slabs must be continuous without gaps")

            if "max_amount" in slab:
                prev_max = Decimal(str(slab["max_amount"]))
            else:
                # Last slab can have no max_amount
                if slab != slabs[-1]:
                    raise ValueError("Only the last slab can have no maximum amount")
                prev_max = Decimal("infinity")

    def validate(self):
        if not isinstance(self.fee_config, dict):
            raise ValueError("Fee config must be a dictionary")

        if "type" not in self.fee_config:
            raise ValueError("Fee type must be specified")

        fee_type = self.fee_config["type"]

        if fee_type not in FeeType.__members__.values():
            raise ValueError(f"Invalid fee type: {fee_type}")

        if fee_type in [FeeType.FIXED, FeeType.PERCENTAGE]:
            if "value" not in self.fee_config:
                raise ValueError("Amount must be specified")

        if fee_type == FeeType.SLAB_BASED:
            if "slabs" not in self.fee_config:
                raise ValueError("Slabs must be specified")
            try:
                self._validate_slabs()
            except Exception as e:
                raise e

        if fee_type == FeeType.SLIDING_SCALE:
            if "slabs" not in self.fee_config:
                raise ValueError("Slabs must be specified")
            for slab in self.fee_config["slabs"]:
                if not all(key in slab for key in ["min_amount", "rate"]):
                    raise ValueError("Each slab must specify min_amount and rate")

        if "min_fee" in self.fee_config and "max_fee" in self.fee_config:
            min_fee = Decimal(str(self.fee_config["min_fee"]))
            max_fee = Decimal(str(self.fee_config["max_fee"]))
            if min_fee > max_fee:
                raise ValueError("Minimum fee cannot be greater than maximum fee")

        if "extra_fee" in self.fee_config:
            if not isinstance(self.fee_config["extra_fee"], dict):
                raise ValueError("Extra fee must be a dictionary")

            if "type" not in self.fee_config["extra_fee"]:
                raise ValueError("Extra fee type must be specified")

            if self.fee_config["extra_fee"]["type"] not in [
                FeeType.FIXED,
                FeeType.PERCENTAGE,
            ]:
                raise ValueError(
                    "Invalid extra fee type. Expected 'fixed' or 'percentage'"
                )

            if "value" not in self.fee_config["extra_fee"]:
                raise ValueError("Value must be specified for extra fee")

            # if self.fee_config["extra_fee"]["type"] == FeeType.PERCENTAGE:
            #     if not 0 <= self.fee_config["extra_fee"]["value"] <= 100:
            #         raise ValueError("Extra fee percentage must be between 0 and 100")

    def _apply_fee_limits(self, fee: Decimal) -> Decimal:
        if "min_fee" in self.fee_config:
            fee = max(fee, Decimal(str(self.fee_config["min_fee"])))

        if "max_fee" in self.fee_config:
            fee = min(fee, Decimal(str(self.fee_config["max_fee"])))

        if "extra_fee" in self.fee_config:
            if self.fee_config["extra_fee"]["type"] == FeeType.PERCENTAGE:
                fee += fee * Decimal(str(self.fee_config["extra_fee"]["value"])) / 100
            elif self.fee_config["extra_fee"]["type"] == FeeType.FIXED:
                fee += Decimal(str(self.fee_config["extra_fee"]))

        return fee

    def _calculate_slab_based_fee(self, amount: Decimal, slabs: list[dict]) -> Decimal:
        total_fee = Decimal("0")
        remaining_amount = amount

        for slab in slabs:
            min_amount = Decimal(str(slab["min_amount"]))
            max_amount = Decimal(str(slab.get("max_amount", float("inf"))))
            rate = Decimal(str(slab["rate"]))

            # Calculate the amount that falls in this slab
            if remaining_amount <= 0:
                break

            slab_amount = min(remaining_amount, max_amount - min_amount)
            slab_fee = slab_amount * rate / 100
            total_fee += slab_fee

            remaining_amount -= slab_amount

        return total_fee

    def calculate_fee(self, amount: Decimal) -> Decimal:
        fee_type = self.fee_config["type"]

        # Calculate base fee
        fee = Decimal("0")

        if fee_type == FeeType.FIXED:
            fee = Decimal(str(self.fee_config["value"]))

        elif fee_type == FeeType.PERCENTAGE:
            fee = amount * Decimal(str(self.fee_config["value"])) / 100

        elif fee_type == FeeType.SLAB_BASED:
            fee = self._calculate_slab_based_fee(amount, self.fee_config["slabs"])

        elif fee_type == FeeType.SLIDING_SCALE:
            _fee = Decimal("0")
            for slab in self.fee_config["slabs"]:
                if amount >= Decimal(str(slab["min_amount"])):
                    _fee = amount * Decimal(str(slab["rate"])) / 100
                else:
                    break
            fee = _fee

        return self._apply_fee_limits(fee)


class PaymentMode(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_credit = models.BooleanField(default=False)
    enabled_for_sales = models.BooleanField(default=True)
    enabled_for_purchase = models.BooleanField(default=True)
    account = models.ForeignKey(
        "ledger.Account",
        on_delete=models.CASCADE,
        related_name="payment_modes",
        blank=True,
        null=True,
    )

    transaction_fee_config = models.JSONField(blank=True, null=True)
    transaction_fee_account = models.ForeignKey(
        "ledger.Account",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="payment_mode_transaction_fee",
    )

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        if not self.is_credit and not self.account:
            raise ValidationError("Account is required for non-credit payment modes")

        if not self.transaction_fee_config:
            return

        try:
            TransactionFeeConfig(self.transaction_fee_config)
        except ValueError as e:
            raise ValidationError({"transaction_fee": str(e)})

        if not self.transaction_fee_account:
            raise ValidationError(
                {
                    "transaction_fee_account": "Transaction fee account is required when transaction fee is enabled"
                }
            )

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Calculate the transaction fee for a given amount"""
        if not self.transaction_fee_config or self.is_credit:
            return Decimal("0")

        return TransactionFeeConfig(self.transaction_fee_config).calculate_fee(amount)

    # TODO: remove float
    def build_ledger_entries(
        self,
        amount: Decimal | float,
        entry_type: Literal["dr", "cr"],
        creditor_account=None,
    ) -> list[list]:
        """Get ledger entries for this payment mode"""

        if entry_type not in ("dr", "cr"):
            raise ValueError("Invalid entry_type; must be either 'dr' or 'cr'")

        # ensure amount is Decimal
        amount = Decimal(str(amount)) if isinstance(amount, float) else amount

        if self.is_credit:
            if not creditor_account:
                raise ValueError("Creditor account is required for credit payment mode")
            return [[entry_type, creditor_account, float(amount)]]

        fee = self.calculate_fee(amount)
        entries = []

        entry_amount = (amount - fee) if entry_type == "dr" else (amount + fee)

        entries.append([entry_type, self.account, float(entry_amount)])

        if fee:
            entries.append([entry_type, self.transaction_fee_account, float(fee)])

        return entries


class Challan(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    issue_datetime = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=CHALLAN_STATUSES)
    remarks = models.TextField(blank=True, null=True)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challan")
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="challan"
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="challan"
    )
    sales_agent = models.ForeignKey(
        SalesAgent,
        blank=True,
        null=True,
        related_name="challan",
        on_delete=models.SET_NULL,
    )
    # Model key for module based permission
    key = "Challan"

    def apply_inventory_transactions(self):
        if self.status == "Draft":
            return

        for row in self.rows.filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            set_inventory_transactions(
                row,
                self.date,
                ["cr", row.item.account, int(row.quantity), 0],
            )

    def mark_as_resolved(self):
        if self.status == "Issued":
            self.status = "Resolved"
            self.save()
        else:
            raise ValueError("This voucher cannot be mark as resolved!")

    class Meta:
        unique_together = ("company", "voucher_no", "fiscal_year")


class ChallanRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(Challan, on_delete=models.CASCADE, related_name="rows")
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="challan_rows"
    )
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    # Model key for module based permission
    key = "Challan"


class SalesVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="sales_invoices",
    )
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    issue_datetime = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)

    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales",
    )

    mode = models.CharField(
        choices=MODES, default=MODES[0][0], max_length=15, null=True, blank=True
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )
    payment_mode = models.ForeignKey(
        PaymentMode, on_delete=models.PROTECT, blank=True, null=True
    )

    challans = models.ManyToManyField(Challan, related_name="sales", blank=True)

    remarks = models.TextField(blank=True, null=True)
    is_export = models.BooleanField(default=False)

    total_amount = models.FloatField(blank=True, null=True)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sales_invoices"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sales_invoices"
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="sales_invoices"
    )
    sales_agent = models.ForeignKey(
        SalesAgent,
        blank=True,
        null=True,
        related_name="sales_invoices",
        on_delete=models.SET_NULL,
    )

    # Model key for module based permission
    key = "Sales"

    class Meta:
        unique_together = ("company", "voucher_no", "fiscal_year")

    @property
    def buyer_name(self):
        if self.party_id:
            return self.party.name
        return self.customer_name

    @property
    def challan_voucher_numbers(self):
        return self.challans.values_list("voucher_no", flat=True)

    def clean(self):
        super().clean()
        if not self.payment_mode.enabled_for_sales:
            raise ValidationError(
                f"Payment mode '{self.payment_mode.name}' is not enabled for sales."
            )

    def apply_inventory_transactions(self):
        challan_enabled = self.company.sales_setting.enable_import_challan
        challan_dct = {}
        if challan_enabled:
            challan_rows = ChallanRow.objects.filter(
                voucher__in=self.challans.all()
            ).values("item_id", "quantity")
            for challan_row in challan_rows:
                challan_dct[challan_row.get("item_id")] = challan_row.get("quantity")
        for row in self.rows.filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            quantity = int(row.quantity)
            if challan_enabled and challan_dct.get(row.item_id):
                quantity = quantity - challan_dct.get(row.item_id)
            if quantity:
                set_inventory_transactions(
                    row,
                    self.date,
                    ["cr", row.item.account, quantity, row.rate],
                )

    def cancel_transactions(self):
        InventoryJournalEntry = apps.get_model("product", "JournalEntry")
        row_ids = self.rows.values_list("id", flat=True)
        JournalEntry.objects.filter(
            Q(object_id__in=[*row_ids], content_type__model="salesvoucherrow")
            | Q(object_id=self.id, content_type__model="salesvoucher"),
        ).delete()
        InventoryJournalEntry.objects.filter(
            content_type__model="salesvoucherrow", object_id__in=row_ids
        ).delete()

    def apply_transactions(self, voucher_meta=None, extra_entries=None):
        voucher_meta = voucher_meta or self.get_voucher_meta()
        if self.total_amount != voucher_meta["grand_total"]:
            self.total_amount = voucher_meta["grand_total"]
            self.save()

        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if self.status == "Draft":
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]

        creditor_account = self.party.customer_account

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(
            sub_total_after_row_discounts
        )

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related(
            "tax_scheme",
            "discount_obj",
            "item__discount_allowed_account",
            "item__sales_account",
        ):
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
                row_dividend_discount = (
                    row_total / sub_total_after_row_discounts
                ) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    sales_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(["dr", row.item.discount_allowed_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(["cr", row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(["cr", row.item.sales_account, sales_value])

            payment_entries = self.payment_mode.build_ledger_entries(
                amount=row_total,
                entry_type="dr",
                creditor_account=creditor_account,
            )

            entries.extend(payment_entries)

            set_ledger_transactions(row, self.date, *entries, clear=True)

        if extra_entries:
            set_ledger_transactions(self, self.date, *extra_entries, clear=True)

        self.apply_inventory_transactions()

    def save(self, *args, **kwargs):
        if self.status not in ["Draft", "Cancelled"] and not self.voucher_no:
            raise ValueError("Issued invoices need a voucher number!")
        super().save(*args, **kwargs)

    def cbms_nepal_data(self, conf):
        meta = self.get_voucher_meta()
        data = {
            "seller_pan": self.company.tax_registration_number,
            "buyer_pan": self.party_tax_reg_no(),
            "buyer_name": self.party_name(),
            "total_sales": meta["grand_total"],
            "taxable_sales_vat": meta["taxable"],
            "vat": meta["tax"],
            "export_sales": 0,
            "tax_exempted_sales": meta["non_taxable"],
            "invoice_number": self.voucher_no,
            "invoice_date": nepdate.string_from_tuple(
                nepdate.ad2bs(str(self.date))
            ).replace("-", "."),
        }
        if self.is_export:
            data["taxable_sales_vat"] = 0
            data["vat"] = 0
            data["export_sales"] = meta["grand_total"]
            data["tax_exempted_sales"] = meta["grand_total"]

        merged_data = dict(merge_dicts(data, conf["data"]))
        merged_data = dict(merge_dicts(merged_data, conf["sales_invoice_data"]))
        return merged_data, conf["sales_invoice_endpoint"]

    @property
    def pdf_url(self):
        return "{}sales-voucher/{}/view?pdf=1".format(settings.BASE_URL, self.pk)

    @property
    def view_url(self):
        return "{}sales-voucher/{}/view".format(settings.BASE_URL, self.pk)

    @property
    def item_names(self):
        # TODO Optimize - SalesBookExportSerializer
        return ", ".join(
            set(
                Item.objects.filter(sales_rows__voucher_id=self.id).values_list(
                    "name", flat=True
                )
            )
        )

    @property
    def units(self):
        # TODO Optimize - SalesBookExportSerializer
        return ", ".join(
            set(
                Unit.objects.filter(sales_rows__voucher_id=self.id).values_list(
                    "name", flat=True
                )
            )
        )


class SalesVoucherRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(
        SalesVoucher, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="sales_rows")
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales_rows",
    )
    rate = models.FloatField()
    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_rows",
    )
    tax_scheme = models.ForeignKey(
        TaxScheme, on_delete=models.CASCADE, related_name="sales_rows"
    )

    # Computed values
    discount_amount = models.FloatField(blank=True, null=True)
    tax_amount = models.FloatField(blank=True, null=True)
    net_amount = models.FloatField(blank=True, null=True)

    # Model key for module based permission
    key = "Sales"

    @property
    def amount_before_tax(self):
        return self.net_amount - self.tax_amount

    @property
    def amount_before_discount(self):
        return self.net_amount - self.tax_amount + self.discount_amount


class PurchaseOrder(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    issue_datetime = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    status = models.CharField(max_length=255, choices=PURCHASE_ORDER_STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)

    print_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="purchase_Orders"
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="purchase_orders"
    )

    # Model key for module based permission
    key = "PurchaseOrder"

    class Meta:
        unique_together = ("company", "voucher_no", "fiscal_year")


class PurchaseOrderRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="purchase_order_rows"
    )
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    # Model key for module based permission
    key = "Purchase Order"


class PurchaseVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.CharField(max_length=25, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchases",
    )

    remarks = models.TextField(blank=True, null=True)
    is_import = models.BooleanField(default=False)

    total_amount = models.FloatField(blank=True, null=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchase_vouchers"
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="purchase_vouchers"
    )
    purchase_orders = models.ManyToManyField(
        PurchaseOrder, related_name="purchases", blank=True
    )

    @property
    def item_names(self):
        # TODO Optimize - PurchaseBookExportSerializer
        return ", ".join(
            set(
                Item.objects.filter(purchase_rows__voucher_id=self.id).values_list(
                    "name", flat=True
                )
            )
        )

    @property
    def units(self):
        # TODO Optimize - PurchaseBookExportSerializer
        return ", ".join(
            set(
                Unit.objects.filter(purchase_rows__voucher_id=self.id).values_list(
                    "name", flat=True
                )
            )
        )

    @property
    def buyer_name(self):
        if self.party_id:
            return self.party.name

    @property
    def purchase_order_numbers(self):
        return self.purchase_orders.values_list("voucher_no", flat=True)

    def find_invalid_transaction(self):
        for row in self.rows.filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ).select_related("item__account"):
            find_obsolete_transactions(
                row,
                self.date,
                ["dr", row.item.account, int(row.quantity)],
            )

    def apply_inventory_transaction(self):
        for row in self.rows.filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            set_inventory_transactions(
                row,
                self.date,
                ["dr", row.item.account, int(row.quantity), row.rate],
            )

    def apply_transactions(self, voucher_meta=None):
        voucher_meta = voucher_meta or self.get_voucher_meta()
        if self.total_amount != voucher_meta["grand_total"]:
            self.total_amount = voucher_meta["grand_total"]
            self.save()

        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if self.status == "Draft":
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == "Credit":
            cr_acc = self.party.supplier_account
        elif self.mode == "Cash":
            cr_acc = get_account(self.company, "Cash")
            self.status = "Paid"
        elif self.mode == "Bank Deposit":
            cr_acc = self.bank_account.ledger
            self.status = "Paid"
        else:
            raise ValueError("No such mode!")

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(
            sub_total_after_row_discounts
        )

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related(
            "tax_scheme",
            "discount_obj",
            "item__discount_received_account",
            "item__purchase_account",
        ):
            entries = []

            row_total = decimalize(row.quantity) * decimalize(row.rate)
            purchase_value = row_total + 0

            row_discount = decimalize(0)
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= decimalize(row_discount_amount)
                if trade_discount:
                    purchase_value -= decimalize(row_discount_amount)
                else:
                    row_discount += decimalize(row_discount_amount)

            if dividend_discount > 0:
                row_dividend_discount = (
                    decimalize(row_total) / decimalize(sub_total_after_row_discounts)
                ) * decimalize(dividend_discount)
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    purchase_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            item = row.item
            if row_discount > 0:
                entries.append(["cr", item.discount_received_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = (
                    decimalize(row.tax_scheme.rate) * decimalize(row_total) / 100
                )
                if row_tax_amount:
                    entries.append(["dr", row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(["dr", item.dr_account, purchase_value])

            entries.append(["cr", cr_acc, row_total])
            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()


class PurchaseVoucherRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(
        PurchaseVoucher, related_name="rows", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, related_name="purchase_rows", on_delete=models.CASCADE
    )
    description = models.TextField(blank=True, null=True)
    quantity = models.FloatField()
    unit = models.ForeignKey(
        Unit,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_rows",
    )
    rate = models.FloatField()

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_rows",
    )

    tax_scheme = models.ForeignKey(
        TaxScheme, blank=True, null=True, on_delete=models.SET_NULL
    )

    # Computed values
    discount_amount = models.FloatField(blank=True, null=True)
    tax_amount = models.FloatField(blank=True, null=True)
    net_amount = models.FloatField(blank=True, null=True)
    key = "PurchaseVoucher"

    def save(self, *args, **kwargs):
        if not self.item.cost_price:
            self.item.cost_price = self.rate
            self.item.save()
        self.send_rate_alert()
        super().save(*args, **kwargs)

    def send_rate_alert(self):
        from django_q.tasks import async_task

        if not self.voucher.company.purchase_setting.enable_item_rate_change_alert:
            return
        rows = self.item.purchase_rows.order_by("-id")
        if rows.exists():
            existing_rate = rows.first().rate
            if existing_rate != self.rate:
                status = "increased" if existing_rate < self.rate else "decreased"
                message = f"The purchase price for {self.item.name} has {status} from {existing_rate} to {self.rate}."
                to_emails = (
                    self.voucher.company.purchase_setting.rate_change_alert_emails
                )
                async_task(
                    "django.core.mail.send_mail",
                    "Item purchase rate change alert.",
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    to_emails,
                )


CREDIT_NOTE_STATUSES = (
    ("Draft", "Draft"),
    ("Issued", "Issued"),
    ("Cancelled", "Cancelled"),
    ("Resolved", "Resolved"),
)


class CreditNote(TransactionModel, InvoiceModel):
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(
        max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0]
    )

    invoices = models.ManyToManyField(SalesVoucher, related_name="credit_notes")

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="credit_notes",
    )
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )

    total_amount = models.FloatField(blank=True, null=True)

    remarks = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="credit_notes"
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="credit_notes"
    )
    print_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("company", "voucher_no", "fiscal_year")

    def cancel(self):
        return super().cancel()

    def apply_inventory_transaction(voucher):
        for row in voucher.rows.filter(is_returned=True).filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            set_inventory_transactions(
                row,
                voucher.date,
                ["dr", row.item.account, int(row.quantity), row.rate],
            )

    def apply_transactions(self):
        voucher_meta = self.get_voucher_meta()

        # import ipdb; ipdb.set_trace()
        if self.total_amount != voucher_meta["grand_total"]:
            self.total_amount = voucher_meta["grand_total"]
            self.save()

        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if self.status == "Draft":
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == "Credit":
            cr_acc = self.party.customer_account
        elif self.mode == "Cash":
            cr_acc = get_account(self.company, "Cash")
            self.status = "Resolved"
        elif self.mode == "Bank Deposit":
            cr_acc = self.bank_account.ledger
            self.status = "Resolved"
        else:
            raise ValueError("No such mode!")

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(
            sub_total_after_row_discounts
        )

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related(
            "tax_scheme",
            "discount_obj",
            "item__discount_allowed_account",
            "item__sales_account",
        ):
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
                row_dividend_discount = (
                    row_total / sub_total_after_row_discounts
                ) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    sales_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(["cr", row.item.discount_allowed_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(["dr", row.tax_scheme.payable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(["dr", row.item.sales_account, sales_value])
            entries.append(["cr", cr_acc, row_total])

            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()

    def cbms_nepal_data(self, conf):
        invoice = self.invoices.first()
        if invoice:
            meta = invoice.get_voucher_meta()
            data = {
                "seller_pan": self.company.tax_registration_number,
                "buyer_pan": self.party_tax_reg_no(),
                "buyer_name": self.party_name(),
                "total_sales": meta["grand_total"],
                "taxable_sales_vat": meta["taxable"],
                "vat": meta["tax"],
                "export_sales": 0,
                "tax_exempted_sales": meta["non_taxable"],
                "ref_invoice_number": invoice.voucher_no,
                "credit_note_number": self.voucher_no,
                "credit_note_date": nepdate.string_from_tuple(
                    nepdate.ad2bs(str(self.date))
                ).replace("-", "."),
                "reason_for_return": self.remarks,
            }
            if invoice.is_export:
                data["taxable_sales_vat"] = 0
                data["vat"] = 0
                data["export_sales"] = meta["grand_total"]
                data["tax_exempted_sales"] = meta["grand_total"]

            merged_data = dict(merge_dicts(data, conf["data"]))
            merged_data = dict(merge_dicts(merged_data, conf["credit_note_data"]))
            return merged_data, conf["credit_note_endpoint"]


class CreditNoteRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(
        CreditNote, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        SalesDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="credit_note_rows",
    )

    tax_scheme = models.ForeignKey(
        TaxScheme, on_delete=models.CASCADE, related_name="credit_note_rows"
    )
    sales_row_data = models.JSONField(blank=True, null=True)


class DebitNote(TransactionModel, InvoiceModel):
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(
        max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0]
    )

    invoices = models.ManyToManyField(PurchaseVoucher, related_name="debit_notes")

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="debit_notes",
    )
    mode = models.CharField(choices=MODES, default=MODES[0][0], max_length=15)
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )

    total_amount = models.FloatField(blank=True, null=True)

    remarks = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="debit_notes")
    fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="debit_notes"
    )
    print_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("company", "voucher_no", "fiscal_year")

    def cancel(self):
        return super().cancel()

    def apply_inventory_transaction(self):
        for row in self.rows.filter(is_returned=True).filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            set_inventory_transactions(
                row,
                self.date,
                ["cr", row.item.account, int(row.quantity), row.rate],
            )

    def apply_transactions(self):
        voucher_meta = self.get_voucher_meta()
        if self.total_amount != voucher_meta["grand_total"]:
            self.total_amount = voucher_meta["grand_total"]
            self.save()

        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if self.status == "Draft":
            return

        # TODO Also keep record of cash payment for party in party ledger [To show transactions for particular party]
        if self.mode == "Credit":
            dr_acc = self.party.supplier_account
        elif self.mode == "Cash":
            dr_acc = get_account(self.company, "Cash")
            self.status = "Resolved"
        elif self.mode == "Bank Deposit":
            dr_acc = self.bank_account.ledger
            self.status = "Resolved"
        else:
            raise ValueError("No such mode!")

        self.save()

        sub_total_after_row_discounts = self.get_total_after_row_discounts()

        dividend_discount, dividend_trade_discount = self.get_discount(
            sub_total_after_row_discounts
        )

        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related(
            "tax_scheme",
            "discount_obj",
            "item__discount_received_account",
            "item__purchase_account",
        ):
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
                row_dividend_discount = (
                    row_total / sub_total_after_row_discounts
                ) * dividend_discount
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    purchase_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            item = row.item
            if row_discount > 0:
                entries.append(["dr", item.discount_received_account, row_discount])

            if row.tax_scheme:
                row_tax_amount = row.tax_scheme.rate * row_total / 100
                if row_tax_amount:
                    entries.append(["cr", row.tax_scheme.receivable, row_tax_amount])
                    row_total += row_tax_amount

            entries.append(["cr", item.dr_account, purchase_value])

            entries.append(["dr", dr_acc, row_total])
            set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transaction()


class DebitNoteRow(TransactionModel, InvoiceRowModel):
    voucher = models.ForeignKey(
        DebitNote, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    rate = models.FloatField()

    discount = models.FloatField(default=0)
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, max_length=15, blank=True, null=True
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="debit_note_rows",
    )

    tax_scheme = models.ForeignKey(
        TaxScheme, on_delete=models.CASCADE, related_name="debit_note_rows"
    )
    purchase_row_data = models.JSONField(blank=True, default=dict)


PAYMENT_MODES = (
    ("Cheque", "Cheque"),
    ("Cash", "Cash"),
    ("Bank Deposit", "Bank Deposit"),
)

PAYMENT_STATUSES = (
    ("Issued", "Issued"),
    ("Cleared", "Cleared"),
    ("Cancelled", "Cancelled"),
)


class PaymentReceipt(TransactionModel):
    invoices = models.ManyToManyField(SalesVoucher, related_name="payment_receipts")
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="payment_receipts"
    )
    date = models.DateField()
    mode = models.CharField(
        choices=PAYMENT_MODES, default=PAYMENT_MODES[0][0], max_length=15
    )
    amount = models.FloatField()
    tds_amount = models.FloatField(default=0)
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUSES, default=PAYMENT_STATUSES[0][0]
    )
    transaction_charge_account = models.ForeignKey(
        TransactionCharge,
        related_name="payment_receipts",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    transaction_charge = models.FloatField(default=0)
    bank_account = models.ForeignKey(
        BankAccount,
        related_name="payment_receipts",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    cheque_deposit = models.ForeignKey(
        ChequeDeposit,
        blank=True,
        null=True,
        related_name="payment_receipts",
        on_delete=models.SET_NULL,
    )
    remarks = models.TextField(blank=True, null=True)
    clearing_date = models.DateField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    @property
    def voucher_no(self):
        return self.id

    def apply_transactions(self, force_update=False):
        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if not self.status == "Cleared":
            return
        if self.mode == "Cheque":
            self.cheque_deposit.apply_transactions()
        elif self.mode == "Cash":
            dr_acc = get_account(self.company, "Cash")
        elif self.mode == "Bank Deposit":
            dr_acc = self.bank_account.ledger
        else:
            raise ValueError("Invalid mode - {}!".format(self.mode))
        entries = []
        cr_amount = 0
        if self.mode != "Cheque":
            entries.append(["dr", dr_acc, self.amount])
            cr_amount += self.amount
        if force_update or self.tds_amount:
            entries.append(
                ["dr", get_account(self.company, "TDS Receivables"), self.tds_amount]
            )
            cr_amount += self.tds_amount
        if cr_amount:
            entries.append(["cr", self.party.customer_account, cr_amount])

        if len(entries):
            set_ledger_transactions(self, self.date, *entries, clear=True)

    def cancel(self, handle_cheque=True):
        self.status = "Cancelled"
        self.save()
        self.cancel_transactions()
        # TODO Revert back invoice status
        if handle_cheque and self.mode == "Cheque":
            self.cheque_deposit.cancel(handle_receipt=False)

    def cancel_transactions(self):
        if not self.status == "Cancelled":
            return
        JournalEntry.objects.filter(
            content_type__model="paymentreceipt", object_id=self.id
        ).delete()

    def clear(self, handle_cheque=True):
        if self.status == "Issued":
            self.status = "Cleared"
            self.clearing_date = datetime.datetime.today()
            self.save()
            total_payment_amount = self.amount + self.tds_amount
            total_invoice_amount = 0
            for invoice in self.invoices.all():
                total_invoice_amount += invoice.total_amount
            if total_payment_amount >= total_invoice_amount:
                self.invoices.update(status="Paid")
            else:
                for invoice in self.invoices.all():
                    total_receipt_amount = 0
                    for receipt in invoice.payment_receipts.filter(status="Cleared"):
                        # Take receipts with single invoices only into account
                        if receipt.invoices.count() == 1:
                            total_receipt_amount += receipt.amount + receipt.tds_amount
                    if total_receipt_amount >= invoice.total_amount:
                        invoice.status = "Paid"
                    else:
                        invoice.status = "Partially Paid"
                    invoice.save()

            if handle_cheque and self.mode == "Cheque":
                self.cheque_deposit.clear(handle_receipt=False)
            self.apply_transactions()
        else:
            raise ValidationError("This receipt cannot be mark as cleared!")

    def journal_entries(self):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = JournalEntry.objects.all().prefetch_related(
            Prefetch(
                "transactions", Transaction.objects.all().select_related("account")
            )
        )
        if self.mode == "Cheque" and self.cheque_deposit_id:
            qs = qs.filter(
                Q(
                    content_type__app_label=app_label,
                    content_type__model=model,
                    object_id=self.id,
                )
                | Q(
                    content_type__app_label="bank",
                    content_type__model="chequedeposit",
                    object_id=self.cheque_deposit_id,
                )
            )
        else:
            qs = qs.filter(
                content_type__app_label=app_label,
                content_type__model=model,
                object_id=self.id,
            )
        return qs

    def __str__(self):
        return str(self.date)


auditlog.register(Challan)
auditlog.register(ChallanRow)
auditlog.register(SalesVoucher)
auditlog.register(SalesVoucherRow)
auditlog.register(PurchaseVoucher)
auditlog.register(PurchaseVoucherRow)
auditlog.register(CreditNote)
auditlog.register(CreditNoteRow)
auditlog.register(DebitNote)
auditlog.register(DebitNoteRow)
