import datetime
import random
import uuid
from copy import deepcopy
from decimal import Decimal
from io import BytesIO
from typing import Union

from auditlog.registry import auditlog
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Prefetch, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import schedule
from apps.quotation.models import Quotation
from weasyprint import HTML

from apps.bank.models import BankAccount, ChequeDeposit
from apps.company.models import Company, CompanyBaseModel, FiscalYear
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
from apps.users.models import User
from apps.voucher.base_models import InvoiceModel, InvoiceRowModel
from awecount.libs import decimalize, nepdate
from awecount.libs.helpers import (
    deserialize_request,
    get_relative_file_path,
    merge_dicts,
    use_miti,
)
from apps.ledger.models.base import Account

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


class TransactionFeeConfig:
    VALID_FEE_TYPES = {"fixed", "percentage", "slab_based", "sliding_scale"}
    VALID_EXTRA_FEE_TYPES = {"fixed", "percentage"}

    def __init__(self, fee_config: dict):
        """
        Initialize the fee configuration.

        Args:
            fee_config: Dictionary containing fee configuration parameters
        """
        # Convert all numeric values to Decimal at initialization
        self.fee_config = self._convert_to_decimal(fee_config)
        self.validate()

    def _convert_to_decimal(self, config: dict) -> dict:
        """Convert all numeric values in the configuration to Decimal."""
        converted = deepcopy(config)

        # Convert direct numeric values
        for key in ["value", "min_fee", "max_fee"]:
            if key in converted:
                converted[key] = Decimal(str(converted[key]))

        # Convert extra fee value if it exists and is not None
        if "extra_fee" in converted and converted["extra_fee"] is not None:
            if "value" in converted["extra_fee"]:
                converted["extra_fee"]["value"] = Decimal(
                    str(converted["extra_fee"]["value"])
                )

        # Convert slab values
        if "slabs" in converted:
            for slab in converted["slabs"]:
                for key in ["min_amount", "max_amount", "rate", "amount"]:
                    if key in slab:
                        slab[key] = Decimal(str(slab[key]))

        return converted

    def validate(self) -> None:
        """Validate the fee configuration."""
        if not isinstance(self.fee_config, dict):
            raise ValueError("Fee config must be a dictionary")

        if "type" not in self.fee_config:
            raise ValueError("Fee type must be specified")

        fee_type = self.fee_config["type"]
        if fee_type not in self.VALID_FEE_TYPES:
            raise ValueError(f"Invalid fee type: {fee_type}")

        # Validate based on fee type
        validators = {
            "fixed": self._validate_simple_fee,
            "percentage": self._validate_simple_fee,
            "slab_based": self._validate_slab_based,
            "sliding_scale": self._validate_sliding_scale,
        }
        validators[fee_type]()
        self._validate_fee_limits()

    def _validate_simple_fee(self) -> None:
        """Validate fixed and percentage fee configurations."""
        if "value" not in self.fee_config:
            raise ValueError("Value must be specified")

    def _validate_slab_based(self) -> None:
        """Validate slab-based fee configuration."""
        if "slabs" not in self.fee_config:
            raise ValueError("Slabs must be specified")

        slabs = self.fee_config["slabs"]
        if not isinstance(slabs, list):
            raise ValueError("Slabs must be a list")

        prev_max = Decimal("0")
        for i, slab in enumerate(slabs):
            if "min_amount" not in slab:
                raise ValueError("Each slab must specify min_amount")

            if ("rate" in slab) == ("amount" in slab):
                raise ValueError(
                    "Each slab must specify either rate or amount, but not both"
                )

            if slab["min_amount"] != prev_max:
                raise ValueError("Slabs must be continuous without gaps")

            if "max_amount" in slab:
                prev_max = slab["max_amount"]
            elif i < len(slabs) - 1:
                raise ValueError("Only the last slab can have no maximum amount")
            else:
                prev_max = Decimal("infinity")

    def _validate_sliding_scale(self) -> None:
        """Validate sliding scale fee configuration."""
        if "slabs" not in self.fee_config:
            raise ValueError("Slabs must be specified")

        slabs = self.fee_config["slabs"]
        if not isinstance(slabs, list):
            raise ValueError("Slabs must be a list")

        for slab in slabs:
            if "min_amount" not in slab:
                raise ValueError("Each slab must specify min_amount")
            if ("rate" in slab) == ("amount" in slab):
                raise ValueError(
                    "Each slab must specify either rate or amount, but not both"
                )

    def _validate_fee_limits(self) -> None:
        """Validate fee limits and extra fee configuration."""
        if "min_fee" in self.fee_config and "max_fee" in self.fee_config:
            if self.fee_config["min_fee"] > self.fee_config["max_fee"]:
                raise ValueError("Minimum fee cannot be greater than maximum fee")

        if "extra_fee" in self.fee_config:
            extra_fee = self.fee_config["extra_fee"]
            if extra_fee is not None:  # Only validate if extra_fee is not None
                if not isinstance(extra_fee, dict):
                    raise ValueError("Extra fee must be a dictionary")

                if "type" not in extra_fee:
                    raise ValueError("Extra fee type must be specified")

                if extra_fee["type"] not in self.VALID_EXTRA_FEE_TYPES:
                    raise ValueError("Invalid extra fee type")

                if "value" not in extra_fee:
                    raise ValueError("Value must be specified for extra fee")

    def calculate_fee(self, amount: Union[Decimal, float, int]) -> Decimal:
        """
        Calculate the fee for a given amount.

        Args:
            amount: The transaction amount

        Returns:
            The calculated fee amount
        """
        amount = Decimal(str(amount))
        fee_type = self.fee_config["type"]

        # Calculate base fee
        calculators = {
            "fixed": self._calculate_fixed_fee,
            "percentage": self._calculate_percentage_fee,
            "slab_based": self._calculate_slab_based_fee,
            "sliding_scale": self._calculate_sliding_scale_fee,
        }

        base_fee = calculators[fee_type](amount)
        return self._apply_fee_limits(base_fee)

    def _calculate_fixed_fee(self, _: Decimal) -> Decimal:
        """Calculate fixed fee."""
        return self.fee_config["value"]

    def _calculate_percentage_fee(self, amount: Decimal) -> Decimal:
        """Calculate percentage-based fee."""
        return amount * self.fee_config["value"] / 100

    def _calculate_slab_based_fee(self, amount: Decimal) -> Decimal:
        """Calculate slab-based fee."""
        total_fee = Decimal("0")
        remaining_amount = amount

        for slab in self.fee_config["slabs"]:
            if remaining_amount <= 0:
                break

            max_amount = slab.get("max_amount", Decimal("infinity"))
            slab_amount = min(remaining_amount, max_amount - slab["min_amount"])

            if "rate" in slab:
                total_fee += slab_amount * slab["rate"] / 100
            else:
                total_fee += slab["amount"]

            remaining_amount -= slab_amount

        return total_fee

    def _calculate_sliding_scale_fee(self, amount: Decimal) -> Decimal:
        """Calculate sliding scale fee."""
        total_fee = Decimal("0")

        for slab in self.fee_config["slabs"]:
            if amount >= slab["min_amount"]:
                if "rate" in slab:
                    total_fee = amount * slab["rate"] / 100
                else:
                    total_fee = slab["amount"]
            else:
                break

        return total_fee

    def _apply_fee_limits(self, fee: Decimal) -> Decimal:
        """Apply minimum, maximum, and extra fee constraints."""
        if "min_fee" in self.fee_config:
            fee = max(fee, self.fee_config["min_fee"])

        if "max_fee" in self.fee_config:
            fee = min(fee, self.fee_config["max_fee"])

        if "extra_fee" in self.fee_config and self.fee_config["extra_fee"] is not None:
            extra_fee = self.fee_config["extra_fee"]
            if extra_fee["type"] == "percentage":
                fee += fee * extra_fee["value"] / 100
            else:  # fixed
                fee += extra_fee["value"]

        return fee


class PaymentMode(CompanyBaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
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

        if not self.transaction_fee_config:
            return

        try:
            TransactionFeeConfig(self.transaction_fee_config)
        except ValueError as e:
            raise ValidationError({"transaction_fee": str(e)})

        if not self.transaction_fee_account and self.transaction_fee_config:
            raise ValidationError(
                {
                    "transaction_fee_account": "Transaction fee account is required when transaction fee is enabled"
                }
            )

    def calculate_fee(self, amount: Decimal | float) -> Decimal:
        """Calculate the transaction fee for a given amount"""
        if not self.transaction_fee_config:
            return Decimal("0")

        if isinstance(amount, float):
            amount = Decimal(str(amount))

        return TransactionFeeConfig(self.transaction_fee_config).calculate_fee(amount)


class Challan(TransactionModel, InvoiceModel, CompanyBaseModel):
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


class ChallanRow(TransactionModel, InvoiceRowModel, CompanyBaseModel):
    voucher = models.ForeignKey(Challan, on_delete=models.CASCADE, related_name="rows")
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="challan_rows"
    )
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("1.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    # Model key for module based permission
    key = "Challan"


class SalesVoucher(TransactionModel, InvoiceModel, CompanyBaseModel):
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
        related_name="sales",
    )

    mode = models.CharField(
        choices=MODES, default=MODES[0][0], max_length=15, null=True, blank=True
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )
    payment_mode = models.ForeignKey(
        PaymentMode,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Payment mode for this sales invoice. Null means it is not paid (credit).",
    )

    challans = models.ManyToManyField(Challan, related_name="sales", blank=True)

    remarks = models.TextField(blank=True, null=True)
    received_by = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    is_export = models.BooleanField(default=False)

    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

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
    quotation = models.OneToOneField(
        Quotation,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_invoice",
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

    def _get_or_create_bank_payment_mode(self, company, bank_account):
        kwargs = {
            "company": company,
            "account": bank_account.ledger,
            "name": bank_account.bank_name or bank_account.account_name,
        }
        if bank_account.commission_account:
            kwargs["transaction_fee_account"] = bank_account.commission_account

        if bank_account.transaction_commission_percent:
            kwargs["transaction_fee_config"] = {
                "type": "percentage",
                "value": bank_account.transaction_commission_percent,
            }

        payment_mode, _ = PaymentMode.objects.get_or_create(**kwargs)
        return payment_mode

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
        if self.payment_mode:
            dr_acc = self.payment_mode.account
            self.status = "Paid"
            self.payment_date = timezone.now().date()
        else:
            if not self.party:
                raise ValueError(
                    "Party is required for sales invoice, when not paid in cash!"
                )
            dr_acc = self.party.customer_account

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

            row_total = decimalize(row.quantity) * decimalize(row.rate)
            sales_value = row_total

            row_discount = decimalize(0)
            if row.has_discount():
                row_discount_amount, trade_discount = row.get_discount()
                row_total -= decimalize(row_discount_amount)
                if trade_discount:
                    sales_value -= decimalize(row_discount_amount)
                else:
                    row_discount += decimalize(row_discount_amount)

            if dividend_discount > 0:
                row_dividend_discount = (
                    row_total / decimalize(sub_total_after_row_discounts)
                ) * decimalize(dividend_discount)
                row_total -= row_dividend_discount
                if dividend_trade_discount:
                    sales_value -= row_dividend_discount
                else:
                    row_discount += row_dividend_discount

            if row_discount > 0:
                entries.append(
                    ["dr", row.item.discount_allowed_account, float(row_discount)]
                )

            if row.tax_scheme:
                row_tax_amount = (
                    decimalize(row.tax_scheme.rate) * row_total / decimalize(100)
                )
                if row_tax_amount:
                    entries.append(
                        ["cr", row.tax_scheme.payable, float(row_tax_amount)]
                    )
                    row_total += row_tax_amount

            entries.append(["cr", row.item.sales_account, float(sales_value)])
            entries.append(["dr", dr_acc, float(row_total)])

            set_ledger_transactions(row, self.date, *entries, clear=True)

        if extra_entries:
            set_ledger_transactions(self, self.date, *extra_entries, clear=True)

        if (
            self.payment_mode
            and (
                commission := self.payment_mode.calculate_fee(
                    voucher_meta["grand_total"]
                )
            )
            and commission > 0
        ):
            commission_entries = [
                ["dr", self.payment_mode.transaction_fee_account, commission],
                ["cr", self.payment_mode.account, commission],
            ]

            set_ledger_transactions(self, self.date, *commission_entries, clear=True)

        self.apply_inventory_transactions()

    def save(self, *args, **kwargs):
        if not self.payment_mode and self.mode == "Cash":
            self.payment_mode = PaymentMode.objects.get_or_create(
                company=self.company, name="Cash"
            )[0]

        elif (
            not self.payment_mode and self.mode == "Bank Deposit" and self.bank_account
        ):
            self.payment_mode = self._get_or_create_bank_payment_mode(
                self.company, self.bank_account
            )

        if self.payment_mode and not self.payment_mode.enabled_for_sales:
            raise ValueError(
                f"Payment mode '{self.payment_mode.name}' is not enabled for sales."
            )

        if self.status not in ["Draft", "Cancelled"] and not self.voucher_no:
            raise ValueError("Issued invoices need a voucher number!")
        super().save(*args, **kwargs)

    def cbms_nepal_data(self, conf):
        meta = self.get_voucher_meta()
        data = {
            "seller_pan": self.company.tax_identification_number,
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

    def email_invoice(self, to, subject, message, attachments, attach_pdf):
        if self.status in ["Draft", "Cancelled"]:
            raise Exception("Draft or Cancelled invoices cannot be sent!")
        pdf_stream = None
        if attach_pdf:
            html_template = render_to_string(
                "sales_invoice_pdf.html",
                {
                    "invoice": {
                        "company": {
                            "name": self.company.name,
                            "address": self.company.address,
                            "contact": self.company.contact_no,
                            "email": ", ".join(self.company.emails),
                            "tax_identification_number": self.company.tax_identification_number,
                            "currency_code": self.company.currency_code,
                        },
                        "billed_to": self.party_name(),
                        "address": self.address,
                        "fiscal_year": self.fiscal_year.name,
                        "date": self.date,
                        "miti": nepdate.string_from_tuple(nepdate.ad2bs(str(self.date)))
                        if use_miti(self.company)
                        else "",
                        "payment_mode": self.payment_mode.name
                        if self.payment_mode
                        else "Credit",
                        "rows": [
                            {
                                "item": {
                                    "hs_code": row.item.category.hs_code
                                    if row.item.category and row.item.category.hs_code
                                    else "",
                                    "name": row.item.name,
                                },
                                "unit": row.unit.name,
                                "quantity": row.quantity,
                                "rate": row.rate,
                                "amount": row.quantity * row.rate,
                            }
                            for row in self.rows.all()
                        ],
                        "in_words": self.amount_in_words,
                        "voucher_meta": self.get_voucher_meta(),
                        "voucher_no": self.voucher_no,
                        "reference": self.reference,
                        "remarks": self.remarks,
                        "received_by": self.received_by,
                    }
                },
            )

            pdf_stream = BytesIO()
            HTML(string=html_template).write_pdf(pdf_stream)
            pdf_stream.seek(0)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
        )
        if attach_pdf:
            email.attach(
                f"Sales Invoice {self.voucher_no}.pdf",
                pdf_stream.getvalue(),
                "application/pdf",
            )

        for attachment in attachments:
            if isinstance(attachment, str):
                file_path = get_relative_file_path(attachment)
                if default_storage.exists(file_path):
                    with default_storage.open(file_path, "rb") as file:
                        email.attach(
                            file_path.split("/")[-1], file.read(), "application/pdf"
                        )
                else:
                    raise ValueError(f"Failed to fetch attachment from {file_path}")
            else:
                email.attach(
                    attachment.name, attachment.file.read(), attachment.content_type
                )

        email.content_subtype = "html"
        email.send()

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


TIME_UNITS = (
    ("Day(s)", "Day(s)"),
    ("Week(s)", "Week(s)"),
    ("Month(s)", "Month(s)"),
    ("Year(s)", "Year(s)"),
)

RECURRING_TEMPLATE_TYPES = (
    ("Sales Voucher", "Sales Voucher"),
    ("Purchase Voucher", "Purchase Voucher"),
)


def add_time_to_date(date, amount, time_unit):
    if time_unit == "Day(s)":
        new_date = date + datetime.timedelta(days=amount)
    elif time_unit == "Week(s)":
        new_date = date + datetime.timedelta(weeks=amount)
    elif time_unit == "Month(s)":
        new_date = date + relativedelta(months=amount)
    elif time_unit == "Year(s)":
        new_date = date + relativedelta(years=amount)
    return new_date


class RecurringVoucherTemplate(CompanyBaseModel):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=25, choices=RECURRING_TEMPLATE_TYPES)
    invoice_data = models.JSONField()
    repeat_interval = models.PositiveSmallIntegerField()
    repeat_interval_time_unit = models.CharField(max_length=10, choices=TIME_UNITS)
    due_date_after = models.PositiveSmallIntegerField()
    due_date_after_time_unit = models.CharField(max_length=10, choices=TIME_UNITS)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    end_after = models.PositiveSmallIntegerField(blank=True, null=True)
    send_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_generated = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    no_of_vouchers_created = models.PositiveSmallIntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.next_date = self.get_next_date()
        if self.pk:
            Schedule.objects.filter(name=f"recurring_voucher_{self.pk}").delete()
        if self.is_active and self.next_date:
            schedule(
                "apps.voucher.models.RecurringVoucherTemplate.generate_voucher",
                self,
                name=f"recurring_voucher_{self.pk}",
                next_run=self.next_date,
                schedule_type="O",
            )
        super().save(*args, **kwargs)

    def get_next_date(self):
        if not self.is_active:
            return None

        if self.end_after and self.no_of_vouchers_created >= self.end_after:
            return None

        if self.last_generated:
            last_date = self.last_generated
            next_date = add_time_to_date(
                last_date, self.repeat_interval, self.repeat_interval_time_unit
            )
            if self.end_date and next_date > self.end_date:
                return None
        else:
            next_date = self.start_date
        return next_date

    @transaction.atomic
    def generate_voucher(self):
        invoice_data = deepcopy(self.invoice_data)

        request = deserialize_request(
            {
                "user": self.user,
                "company": self.company,
                "company_id": self.company.id,
                "user_id": self.user.id,
                "data": invoice_data,
            }
        )
        if self.type == "Sales Voucher":
            from apps.voucher.serializers.sales import SalesVoucherCreateSerializer

            invoice_data["date"] = self.next_date
            invoice_data["due_date"] = add_time_to_date(
                self.next_date, self.due_date_after, self.due_date_after_time_unit
            )
            invoice_data["status"] = "Issued"
            serializer = SalesVoucherCreateSerializer(
                data=invoice_data,
                context={
                    "request": request,
                },
            )
            serializer.is_valid(raise_exception=True)
            voucher = serializer.save()
        else:
            from apps.voucher.serializers.purchase import (
                PurchaseVoucherCreateSerializer,
            )

            invoice_data["date"] = self.next_date
            invoice_data["due_date"] = add_time_to_date(
                self.next_date, self.due_date_after, self.due_date_after_time_unit
            )
            invoice_data["status"] = "Issued"
            invoice_data["voucher_no"] = "auto-{}-{}-{}".format(
                self.id, self.no_of_vouchers_created + 1, random.randint(1000, 9999)
            )
            voucher = PurchaseVoucherCreateSerializer(
                data=invoice_data,
                context={
                    "request": request,
                },
            )
            voucher.is_valid(raise_exception=True)
            voucher = voucher.save()

        if self.send_email:
            success_message = f"""
            <html>
                <body>
                    <h1>Recurring {self.type} Generated Successfully</h1>
                    <p>Dear {self.user.full_name},</p>
                    <p>We are pleased to inform you that the recurring {self.type.lower()} titled <strong>{self.title}</strong> has been successfully generated.</p>
                <p>You can view the generated voucher in the dashboard. If you encounter any issues, please contact us.</p>
                </body>
            </html>
            """

            email = EmailMessage(
                subject="Recurring Voucher Generated Successfully",
                body=success_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.user.email],
            )
            email.content_subtype = "html"
            email.send()

        self.no_of_vouchers_created += 1
        self.last_generated = self.next_date
        self.save()


class SalesVoucherRow(TransactionModel, InvoiceRowModel, CompanyBaseModel):
    voucher = models.ForeignKey(
        SalesVoucher, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="sales_rows")
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
        related_name="sales_rows",
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
        related_name="sales_rows",
    )
    tax_scheme = models.ForeignKey(
        TaxScheme,
        on_delete=models.CASCADE,
        related_name="sales_rows",
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
    key = "Sales"

    @property
    def amount_before_tax(self):
        return self.net_amount - self.tax_amount

    @property
    def amount_before_discount(self):
        return self.net_amount - self.tax_amount + self.discount_amount


class PurchaseOrder(TransactionModel, InvoiceModel, CompanyBaseModel):
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
    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("1.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    # Model key for module based permission
    key = "Purchase Order"


class PurchaseVoucher(TransactionModel, InvoiceModel, CompanyBaseModel):
    voucher_no = models.CharField(max_length=25, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=15)
    mode = models.CharField(
        choices=MODES, default=MODES[0][0], max_length=15, blank=True, null=True
    )
    payment_mode = models.ForeignKey(
        PaymentMode,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Payment mode for this purchase. Null means it is not paid (credit).",
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
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
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchases",
    )

    remarks = models.TextField(blank=True, null=True)
    is_import = models.BooleanField(default=False)

    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

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

    def save(self, *args, **kwargs):
        if self.payment_mode and not self.payment_mode.enabled_for_purchase:
            raise ValidationError(
                f"Payment mode '{self.payment_mode.name}' is not enabled for purchase."
            )
        super().save(*args, **kwargs)

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
        if self.payment_mode:
            cr_acc = self.payment_mode.account
            self.status = "Paid"
        else:
            cr_acc = self.party.supplier_account

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

        if (
            self.payment_mode
            and (
                commission := self.payment_mode.calculate_fee(
                    voucher_meta["grand_total"]
                )
            )
            and commission > 0
        ):
            commission_entries = [
                ["dr", self.payment_mode.transaction_fee_account, commission],
                ["cr", self.payment_mode.account, commission],
            ]

            set_ledger_transactions(self, self.date, *commission_entries, clear=True)

        if self.company.purchase_setting.enable_landed_cost:
            # TODO Optmiziation: Create account map outside the loop
            account_map = {}
            landed_cost_accounts = self.company.purchase_setting.landed_cost_accounts
            for landed_cost in self.landed_cost_rows.all():
                entries = []
                if landed_cost.type == LandedCostRowType.CUSTOMS_VALUATION_UPLIFT:
                    # Only account tax amount of uplifted value
                    if landed_cost.tax_scheme and landed_cost.tax_scheme.rate:
                        credit_account = landed_cost.credit_account
                        if not credit_account:
                            raise ValidationError("Credit account is required for customs valuation uplift when tax is applied")
                        account = landed_cost.tax_scheme.receivable
                        entries.append(["dr", account, landed_cost.tax_amount])
                        entries.append(
                            [
                                "cr",
                                landed_cost.credit_account,
                                landed_cost.tax_amount,
                            ]
                        )
                elif landed_cost.type == LandedCostRowType.TAX_ON_PURCHASE:
                    account = landed_cost.tax_scheme.receivable
                    entries.append(["dr", account, landed_cost.amount])
                    entries.append(
                        [
                            "cr",
                            landed_cost.credit_account,
                            landed_cost.amount,
                        ]
                    )
                else:
                    account = account_map.get(landed_cost.type, None)
                    if not account:
                        account = Account.objects.get(
                            id=landed_cost_accounts[landed_cost.type],
                            company_id=self.company_id,
                        )
                        account_map[landed_cost.type] = account

                    entries.append(["dr", account, landed_cost.amount])

                    row_tax_amount = Decimal("0.00")

                    if landed_cost.tax_scheme:
                        row_tax_amount = (
                            landed_cost.tax_scheme.rate * landed_cost.amount / Decimal(100)
                        )
                        if row_tax_amount:
                            entries.append(
                                ["dr", landed_cost.tax_scheme.receivable, row_tax_amount]
                            )

                    entries.append(
                        [
                            "cr",
                            landed_cost.credit_account,
                            landed_cost.amount + row_tax_amount,
                        ]
                    )
                set_ledger_transactions(landed_cost, self.date, *entries, clear=True)

        self.apply_inventory_transaction()

    def journal_entries(self):
        # Also include landed cost rows in the journal entries
        landed_cost_ids = self.landed_cost_rows.values_list("id", flat=True)
        landed_cost_kwargs = {
            "content_type__model": "landedcostrow",
            "object_id__in": landed_cost_ids,
        }
        return super().journal_entries(additional_kwargs=landed_cost_kwargs)


class PurchaseVoucherRow(TransactionModel, InvoiceRowModel, CompanyBaseModel):
    voucher = models.ForeignKey(
        PurchaseVoucher, related_name="rows", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, related_name="purchase_rows", on_delete=models.CASCADE
    )
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    unit = models.ForeignKey(
        Unit,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_rows",
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
        choices=DISCOUNT_TYPES,
        max_length=15,
        null=True,
        blank=True,
    )
    trade_discount = models.BooleanField(default=False)
    discount_obj = models.ForeignKey(
        PurchaseDiscount,
        null=True,
        blank=True,
        related_name="purchase_rows",
        on_delete=models.SET_NULL,
    )

    tax_scheme = models.ForeignKey(
        TaxScheme, blank=True, null=True, on_delete=models.SET_NULL
    )

    # Computed values
    discount_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    tax_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    net_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
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


class CreditNote(TransactionModel, InvoiceModel, CompanyBaseModel):
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(
        max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0]
    )

    invoices = models.ManyToManyField(SalesVoucher, related_name="credit_notes")

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
        related_name="credit_notes",
    )
    mode = models.CharField(
        choices=MODES, default=MODES[0][0], max_length=15, blank=True, null=True
    )
    payment_mode = models.ForeignKey(
        PaymentMode,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Payment mode for this credit note. Null means it is not paid (credit).",
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )

    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

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

    def apply_transactions(self, extra_entries=None):
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
        if self.payment_mode:
            cr_acc = self.payment_mode.account
            self.status = "Resolved"
        else:
            cr_acc = self.party.customer_account

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

        if extra_entries:
            set_ledger_transactions(self, self.date, *extra_entries, clear=True)

        if (
            self.payment_mode
            and (
                commission := self.payment_mode.calculate_fee(
                    voucher_meta["grand_total"]
                )
            )
            and commission > 0
        ):
            commission_entries = [
                ["dr", self.payment_mode.transaction_fee_account, commission],
                ["cr", self.payment_mode.account, commission],
            ]

            set_ledger_transactions(self, self.date, *commission_entries, clear=True)

        self.apply_inventory_transaction()

    def cbms_nepal_data(self, conf):
        invoice = self.invoices.first()
        if invoice:
            meta = invoice.get_voucher_meta()
            data = {
                "seller_pan": self.company.tax_identification_number,
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


class CreditNoteRow(TransactionModel, InvoiceRowModel, CompanyBaseModel):
    voucher = models.ForeignKey(
        CreditNote, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

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
        related_name="credit_note_rows",
    )

    tax_scheme = models.ForeignKey(
        TaxScheme, on_delete=models.CASCADE, related_name="credit_note_rows"
    )
    sales_row_data = models.JSONField(blank=True, null=True)


class DebitNote(TransactionModel, InvoiceModel, CompanyBaseModel):
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)

    voucher_no = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    status = models.CharField(
        max_length=25, choices=CREDIT_NOTE_STATUSES, default=CREDIT_NOTE_STATUSES[0][0]
    )

    invoices = models.ManyToManyField(PurchaseVoucher, related_name="debit_notes")

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
        PurchaseDiscount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="debit_notes",
    )
    mode = models.CharField(
        choices=MODES, default=MODES[0][0], max_length=15, blank=True, null=True
    )
    payment_mode = models.ForeignKey(
        PaymentMode,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Payment mode for this debit note. Null means it is not paid (credit).",
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, on_delete=models.SET_NULL
    )

    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

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
        if self.payment_mode:
            dr_acc = self.payment_mode.account
            self.status = "Resolved"
        else:
            dr_acc = self.party.supplier_account

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

        if (
            self.payment_mode
            and (
                commission := self.payment_mode.calculate_fee(
                    voucher_meta["grand_total"]
                )
            )
            and commission > 0
        ):
            commission_entries = [
                ["dr", self.payment_mode.transaction_fee_account, commission],
                ["cr", self.payment_mode.account, commission],
            ]

            set_ledger_transactions(self, self.date, *commission_entries, clear=True)

        self.apply_inventory_transaction()


class DebitNoteRow(TransactionModel, InvoiceRowModel, CompanyBaseModel):
    voucher = models.ForeignKey(
        DebitNote, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_returned = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
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


class PaymentReceipt(TransactionModel, CompanyBaseModel):
    invoices = models.ManyToManyField(SalesVoucher, related_name="payment_receipts")
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="payment_receipts"
    )
    date = models.DateField()
    mode = models.CharField(
        choices=PAYMENT_MODES, default=PAYMENT_MODES[0][0], max_length=15
    )
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    tds_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUSES,
        default=PAYMENT_STATUSES[0][0],
    )
    transaction_charge_account = models.ForeignKey(
        TransactionCharge,
        related_name="payment_receipts",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    transaction_charge = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
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
        acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if not self.status == "Cleared":
            return
        if self.mode == "Cheque":
            self.cheque_deposit.apply_transactions()
        elif self.mode == "Cash":
            dr_acc = get_account(self.company, acc_system_codes.get("Cash"))
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
                [
                    "dr",
                    get_account(self.company, acc_system_codes.get("TDS Receivables")),
                    self.tds_amount,
                ]
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


IMPORT_TYPES = (
    ("Sales Voucher", "Sales Voucher"),
    ("Purchase Voucher", "Purchase Voucher"),
    ("Credit Note", "Credit Note"),
    ("Debit Note", "Debit Note"),
    ("Item", "Item"),
    ("Party", "Party"),
)

IMPORT_STATUSES = (
    ("Pending", "Pending"),
    ("Completed", "Completed"),
    ("Failed", "Failed"),
)


class Import(models.Model):
    def get_path(self, filename):
        return "imports/{}.{}".format(uuid.uuid4(), filename.split(".")[-1])

    file = models.FileField(upload_to=get_path)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type = models.CharField(choices=IMPORT_TYPES, max_length=25)
    status = models.CharField(choices=IMPORT_STATUSES, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class LandedCostRowType(models.TextChoices):
    DUTY = "Duty"
    LABOR = "Labor"
    FREIGHT = "Freight"
    INSURANCE = "Insurance"
    BROKERAGE = "Brokerage"
    STORAGE = "Storage"
    PACKAGING = "Packaging"
    LOADING = "Loading"
    UNLOADING = "Unloading"
    REGULATORY_FEE = "Regulatory Fee"
    CUSTOMS_DECLARATION = "Customs Declaration"
    OTHER_CHARGES = "Other Charges"
    TAX_ON_PURCHASE = "Tax on Purchase"
    CUSTOMS_VALUATION_UPLIFT = "Customs Valuation Uplift"


class LandedCostRow(models.Model):
    type = models.CharField(choices=LandedCostRowType.choices, max_length=25)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=24, decimal_places=6)
    value = models.DecimalField(max_digits=24, decimal_places=6)
    is_percentage = models.BooleanField(default=False)
    invoice = models.ForeignKey(
        PurchaseVoucher,
        on_delete=models.CASCADE,
        related_name="landed_cost_rows",
    )
    tax_scheme = models.ForeignKey(
        TaxScheme,
        on_delete=models.CASCADE,
        related_name="landed_cost_rows",
        null=True,
        blank=True,
    )
    credit_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="landed_cost_rows",
        blank=True,
        null=True,
        help_text="Account to which the landed cost will be credited",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tax_amount = models.DecimalField(
        max_digits=24, decimal_places=6, default=Decimal("0")
    )
    total_amount = models.DecimalField(
        max_digits=24, decimal_places=6, default=Decimal("0")
    )

    def get_voucher_no(self):
        return self.invoice.voucher_no

    @property
    def voucher(self):
        return self.invoice

    @property
    def voucher_no(self):
        return self.invoice.voucher_no

    @property
    def voucher_id(self):
        return self.invoice.pk

    def get_source_id(self):
        return self.invoice.pk

    def save(self, *args, **kwargs):
        if self.type == LandedCostRowType.TAX_ON_PURCHASE or not self.tax_scheme:
            self.tax_amount = Decimal("0")
            self.total_amount = self.amount
        else:
            self.tax_amount = self.tax_scheme.rate * self.amount / Decimal("100")
            self.total_amount = self.amount + self.tax_amount

        super().save(*args, **kwargs)


# class LandingCostDistribution(models.Model):
#     landing_cost_row = models.ForeignKey(
#         LandingCostRow,
#         on_delete=models.CASCADE,
#         related_name="distributions",
#     )
#     invoice_row = models.ForeignKey(
#         PurchaseVoucherRow,
#         on_delete=models.CASCADE,
#         related_name="landing_cost_distributions",
#     )
#     amount = models.DecimalField(max_digits=24, decimal_places=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


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
