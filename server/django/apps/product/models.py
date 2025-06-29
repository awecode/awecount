from collections import OrderedDict
from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models import F, Func, JSONField, Q, Sum, Value, Window
from django.db.models.functions import Cast, Coalesce
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

from apps.company.models import Company, CompanyBaseModel
from apps.ledger.models import (
    Account,
    TransactionModel,
    get_account,
)
from apps.ledger.models import Category as AccountCategory
from apps.ledger.models import Transaction as LedgerTransaction
from apps.ledger.models import set_transactions as set_ledger_transactions
from apps.tax.models import TaxScheme
from apps.voucher.base_models import InvoiceModel, InvoiceRowModel
from awecount.libs import zero_for_none
from awecount.libs.helpers import jsonify

acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES

class Unit(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    @staticmethod
    def create_default_units(company):
        units = [
            Unit(name="Piece(s)", short_name="pcs", company=company),
            Unit(name="Unit(s)", short_name="unit", company=company),
        ]
        return Unit.objects.bulk_create(units)

    def __str__(self):
        return self.short_name or self.name

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("short_name", "company")
        ordering = ["-id"]


LEDGER_TYPES = [
    ("dedicated", "Use dedicated account"),
    ("global", "Use global account"),
    ("existing", "Use existing account"),
    ("category", "Use category specific account"),
    ("creation", "Choose during item creation"),
]

ITEM_TYPES = (
    ("Tangible Sellable", "Tangible Sellable"),
    ("Intangible Sellable", "Intangible Sellable"),
    ("Expense", "Expense"),
    ("Asset", "Asset"),
)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="brands"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]


class Category(CompanyBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    default_unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.SET_NULL
    )
    hs_code = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1000)],
    )
    default_tax_scheme = models.ForeignKey(
        TaxScheme,
        blank=True,
        null=True,
        related_name="categories",
        on_delete=models.SET_NULL,
    )

    sales_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_categories",
    )
    purchase_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_categories",
    )
    discount_allowed_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_allowed_categories",
    )
    discount_received_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_received_categories",
    )

    sales_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_item_categories",
    )
    purchase_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_item_categories",
    )
    discount_allowed_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_allowed_item_categories",
    )
    discount_received_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_received_item_categories",
    )
    fixed_asset_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="fixed_asset_account_category",
    )
    direct_expense_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="direct_expense_account_category",
    )
    indirect_expense_account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="indirect_expense_account_category",
    )

    items_sales_account_type = models.CharField(
        max_length=100, choices=LEDGER_TYPES, null=True, blank=True
    )
    items_purchase_account_type = models.CharField(
        max_length=100, choices=LEDGER_TYPES, null=True, blank=True
    )
    items_discount_allowed_account_type = models.CharField(
        max_length=100, choices=LEDGER_TYPES, null=True, blank=True
    )
    items_discount_received_account_type = models.CharField(
        max_length=100, choices=LEDGER_TYPES, null=True, blank=True
    )

    dedicated_sales_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sales_categories_dedicated",
    )
    dedicated_purchase_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_categories_dedicated",
    )
    dedicated_discount_allowed_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_allowed_categories_dedicated",
    )
    dedicated_discount_received_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_received_categories_dedicated",
    )

    # type = models.CharField(max_length=20, choices=ITEM_TYPES)
    track_inventory = models.BooleanField(default=True)
    can_be_sold = models.BooleanField(default=True)
    can_be_purchased = models.BooleanField(default=True)
    fixed_asset = models.BooleanField(default=False)
    direct_expense = models.BooleanField(default=False)
    indirect_expense = models.BooleanField(default=False)

    extra_fields = JSONField(default=list, null=True, blank=True)
    # {'name': 'Author', 'type': 'Text/Number/Date/Long Text', 'enable_search': 'false/true'}

    use_account_subcategory = models.BooleanField(default=False)
    account_category = models.ForeignKey(
        AccountCategory,
        blank=True,
        null=True,
        related_name="item_categories",
        on_delete=models.SET_NULL,
    )

    # Required for module-wise permission check
    key = "InventoryCategory"

    def suggest_code(self, prefix=None):
        self.code = self.name.lower().replace(" ", "-")

    def get_account_category(self, default_system_code, prefix=""):
        acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
        if (
            default_system_code
            in [
                acc_cat_system_codes["Fixed Assets"],
                acc_cat_system_codes["Direct Expenses"],
                acc_cat_system_codes["Indirect Expenses"],
            ]
            and self.account_category_id
            and self.account_category
        ):
            parent_account_category = self.account_category
        else:
            parent_account_category = AccountCategory.objects.get(
                system_code=default_system_code, company=self.company
            )

        if self.use_account_subcategory:
            name = self.name
            if prefix:
                name = "{} - {}".format(prefix, name)
            account_category = AccountCategory(name=name, company=self.company)
            account_category.set_parent(parent_account_category)
            code = account_category.suggest_code(self, prefix="C")
            try:
                with transaction.atomic():
                    account_category.save()
            except IntegrityError:
                account_category = AccountCategory.objects.get(
                    code=code, company=self.company
                )
                if account_category.name != name:
                    account_category.name = name
                    account_category.save()
            return account_category
        else:
            return parent_account_category

    def save(self, *args, **kwargs):
        self.validate_unique()
        post_save = kwargs.pop("post_save", True)
        if not self.code:
            self.suggest_code()
        super().save(*args, **kwargs)

        if post_save:
            sales_account_name = self.name + " (Sales)"
            discount_allowed_account_name = "Discount Allowed - " + self.name
            purchase_account_name = self.name + " (Purchase)"
            discount_received_account_name = "Discount Received - " + self.name

            acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES

            # Update dedicated accounts
            if self.dedicated_sales_account:
                if not self.dedicated_sales_account.name == sales_account_name:
                    self.dedicated_sales_account.name = sales_account_name
                    self.dedicated_sales_account.save()

            if self.dedicated_purchase_account:
                if not self.dedicated_purchase_account.name == purchase_account_name:
                    self.dedicated_purchase_account.name = purchase_account_name
                    self.dedicated_purchase_account.save()

            if self.dedicated_discount_allowed_account:
                if (
                    not self.dedicated_discount_allowed_account.name
                    == discount_allowed_account_name
                ):
                    self.dedicated_discount_allowed_account.name = (
                        discount_allowed_account_name
                    )
                    self.dedicated_discount_allowed_account.save()

            if self.dedicated_discount_received_account:
                if (
                    not self.dedicated_discount_received_account.name
                    == discount_received_account_name
                ):
                    self.dedicated_discount_received_account.name = (
                        discount_received_account_name
                    )
                    self.dedicated_discount_received_account.save()

            # if self.can_be_sold:
            if not self.sales_account:
                if not self.dedicated_sales_account:
                    ledger = Account(name=sales_account_name, company=self.company)
                    ledger.add_category(acc_cat_system_codes["Sales"])
                    # account_category = self.get_account_category("Sales", prefix="Sales")
                    # ledger.category = account_category
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    self.sales_account = ledger
                    self.dedicated_sales_account = ledger
                else:
                    self.sales_account = self.dedicated_sales_account

            if not self.discount_allowed_account:
                if not self.dedicated_discount_allowed_account:
                    discount_allowed_account = Account(
                        name=discount_allowed_account_name, company=self.company
                    )
                    discount_allowed_account.add_category(
                        acc_cat_system_codes["Discount Expenses"]
                    )
                    # account_category = self.get_account_category('Discount Expenses', prefix='Discount Allowed')
                    # discount_allowed_account.category = account_category
                    discount_allowed_account.suggest_code(self, prefix="C")
                    discount_allowed_account.save()
                    self.discount_allowed_account = discount_allowed_account
                    self.dedicated_discount_allowed_account = discount_allowed_account
                else:
                    self.discount_allowed_account = (
                        self.dedicated_discount_allowed_account
                    )

            # if self.can_be_purchased:
            if not self.purchase_account:
                if not self.dedicated_purchase_account:
                    ledger = Account(name=purchase_account_name, company=self.company)
                    ledger.add_category(acc_cat_system_codes["Purchase"])
                    # account_category = self.get_account_category('Purchase', prefix='Purchase')
                    # ledger.category = account_category
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    self.purchase_account = ledger
                    self.dedicated_purchase_account = ledger
                else:
                    self.purchase_account = self.dedicated_purchase_account

            if not self.discount_received_account:
                if not self.dedicated_discount_received_account:
                    discount_received_account = Account(
                        name=discount_received_account_name, company=self.company
                    )
                    discount_received_account.add_category(
                        acc_cat_system_codes["Discount Income"]
                    )
                    # account_category = self.get_account_category('Discount Income', prefix='Discount Received')
                    # discount_received_account.category = account_category
                    discount_received_account.suggest_code(self, prefix="C")
                    discount_received_account.save()
                    self.discount_received_account = discount_received_account
                    self.dedicated_discount_received_account = discount_received_account
                else:
                    self.discount_received_account = (
                        self.dedicated_discount_received_account
                    )

            # Set/Update account categories

            if self.can_be_sold:
                account_category = self.get_account_category(
                    acc_cat_system_codes["Sales"], prefix="Sales"
                )
                self.sales_account_category = account_category
                Account.objects.filter(sales_item__category=self).update(
                    category=account_category
                )
                account_category = self.get_account_category(
                    acc_cat_system_codes["Discount Expenses"],
                    prefix="Discount Allowed",
                )
                self.discount_allowed_account_category = account_category
                Account.objects.filter(discount_allowed_item__category=self).update(
                    category=account_category
                )

            if self.can_be_purchased:
                account_category = self.get_account_category(
                    acc_cat_system_codes["Purchase"], prefix="Purchase"
                )
                self.purchase_account_category = account_category
                Account.objects.filter(purchase_item__category=self).update(
                    category=account_category
                )
                account_category = self.get_account_category(
                    acc_cat_system_codes["Discount Income"],
                    prefix="Discount Received",
                )
                self.discount_received_account_category = account_category
                Account.objects.filter(discount_received_item__category=self).update(
                    category=account_category
                )

            if self.direct_expense:
                account_category = self.get_account_category(
                    acc_cat_system_codes["Direct Expenses"]
                )
                self.direct_expense_account_category = account_category
                Account.objects.filter(expense_item__category=self).update(
                    category=account_category
                )
            elif self.indirect_expense:
                account_category = self.get_account_category(
                    acc_cat_system_codes["Indirect Expenses"]
                )
                self.indirect_expense_account_category = account_category
                Account.objects.filter(expense_item__category=self).update(
                    category=account_category
                )
            elif self.fixed_asset:
                account_category = self.get_account_category(
                    acc_cat_system_codes["Fixed Assets"]
                )
                self.fixed_asset_account_category = account_category
                Account.objects.filter(fixed_asset_item__category=self).update(
                    category=account_category
                )

            # TODO Optimize
            # AccountTransaction.objects.filter()
            # Maybe required if category is changed
            # from apps.voucher.models import PurchaseVoucher, SalesVoucher

            # for voucher in PurchaseVoucher.objects.filter(rows__item__category=self):
            #     voucher.apply_transactions()
            #
            # for voucher in SalesVoucher.objects.filter(rows__item__category=self):
            #     voucher.apply_transactions()

            # if self.use_account_subcategory and self.account_category_id and self.account_category:
            #     with transaction.atomic():
            #         AccountCategory.objects.rebuild()
            self.save(post_save=False)

    def apply_account_settings_to_items(self):
        sales_account = None
        discount_allowed_account = None
        purchase_account = None
        discount_received_account = None

        acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
        acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
        if self.can_be_sold:
            if self.items_sales_account_type == "global":
                sales_account = Account.objects.get(
                    system_code=acc_system_codes["Sales Account"],
                    company=self.company,
                )
            elif self.items_sales_account_type == "existing":
                sales_account = self.sales_account
            elif self.items_sales_account_type == "category":
                if not self.dedicated_sales_account:
                    sales_account_name = self.name + " (Sales)"
                    ledger = Account(name=sales_account_name, company=self.company)
                    ledger.add_category(
                        acc_cat_system_codes["Sales"],
                    )
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    sales_account = ledger
                else:
                    sales_account = self.dedicated_sales_account

            if self.items_discount_allowed_account_type == "global":
                discount_allowed_account = Account.objects.get(
                    system_code=acc_system_codes["Discount Expenses"],
                    company=self.company,
                )
            elif self.items_discount_allowed_account_type == "existing":
                discount_allowed_account = self.discount_allowed_account
            elif self.items_discount_allowed_account_type == "category":
                if not self.dedicated_discount_allowed_account:
                    discount_allowed_account_name = "Discount Allowed - " + self.name
                    ledger = Account(
                        name=discount_allowed_account_name, company=self.company
                    )
                    ledger.add_category(acc_cat_system_codes["Discount Expenses"])
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    discount_allowed_account = ledger
                else:
                    discount_allowed_account = self.dedicated_discount_allowed_account

        if self.can_be_purchased:
            if self.items_purchase_account_type == "global":
                purchase_account = Account.objects.get(
                    system_code=acc_system_codes["Purchase Account"],
                    company=self.company,
                )
            elif self.items_purchase_account_type == "existing":
                purchase_account = self.purchase_account
            elif self.items_purchase_account_type == "category":
                if not self.dedicated_purchase_account:
                    purchase_account_name = self.name + " (Purchase)"
                    ledger = Account(name=purchase_account_name, company=self.company)
                    ledger.add_category(acc_cat_system_codes["Purchase"])
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    purchase_account = ledger
                else:
                    purchase_account = self.dedicated_purchase_account

            if self.items_discount_received_account_type == "global":
                discount_received_account = Account.objects.get(
                    system_code=acc_system_codes["Discount Income"],
                    company=self.company,
                )
            elif self.items_discount_received_account_type == "existing":
                discount_received_account = self.discount_received_account
            elif self.items_discount_received_account_type == "category":
                if not self.dedicated_discount_received_account:
                    discount_received_account_name = "Discount Received - " + self.name
                    ledger = Account(
                        name=discount_received_account_name, company=self.company
                    )
                    ledger.add_category(acc_cat_system_codes["Discount Expenses"])
                    ledger.suggest_code(self, prefix="C")
                    ledger.save()
                    discount_received_account = ledger
                else:
                    discount_received_account = self.dedicated_discount_received_account
        # To prevent curcular import
        from apps.voucher.models import (
            CreditNoteRow,
            DebitNoteRow,
            PurchaseVoucherRow,
            SalesVoucherRow,
        )

        update_fields = {}
        if sales_account is not None:
            update_fields["sales_account"] = sales_account
            update_fields["sales_account_type"] = self.items_sales_account_type
        if discount_allowed_account is not None:
            update_fields["discount_allowed_account"] = discount_allowed_account
            update_fields["discount_allowed_account_type"] = (
                self.items_discount_allowed_account_type
            )
        if purchase_account is not None:
            update_fields["purchase_account"] = purchase_account
            update_fields["purchase_account_type"] = self.items_purchase_account_type
        if discount_received_account is not None:
            update_fields["discount_received_account"] = discount_received_account
            update_fields["discount_received_account_type"] = (
                self.items_discount_received_account_type
            )
        if update_fields:
            items_list = Item.objects.filter(
                category=self, company=self.company
            ).select_related(
                "sales_account",
                "purchase_account",
                "discount_allowed_account",
                "discount_received_account",
            )
            for item in items_list:
                sales_voucher_row_ids = SalesVoucherRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                credit_note_row_ids = CreditNoteRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                purchase_voucher_row_ids = PurchaseVoucherRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                debit_note_row_ids = DebitNoteRow.objects.filter(item=item).values_list(
                    "id", flat=True
                )
                if sales_account:
                    LedgerTransaction.objects.filter(
                        journal_entry__object_id__in=[
                            *sales_voucher_row_ids,
                            *credit_note_row_ids,
                        ],
                        journal_entry__content_type__model__in=[
                            "salesvoucherrow",
                            "creditnoterow",
                        ],
                        account=item.sales_account,
                    ).update(account=sales_account)

                if discount_allowed_account:
                    LedgerTransaction.objects.filter(
                        journal_entry__object_id__in=[
                            *sales_voucher_row_ids,
                            *credit_note_row_ids,
                        ],
                        journal_entry__content_type__model__in=[
                            "salesvoucherrow",
                            "creditnoterow",
                        ],
                        account=item.discount_allowed_account,
                    ).update(account=discount_allowed_account)

                if purchase_account:
                    LedgerTransaction.objects.filter(
                        journal_entry__object_id__in=[
                            *purchase_voucher_row_ids,
                            *debit_note_row_ids,
                        ],
                        journal_entry__content_type__model__in=[
                            "purchasevoucherrow",
                            "debitnoterow",
                        ],
                        account=item.purchase_account,
                    ).update(account=purchase_account)

                if discount_received_account:
                    LedgerTransaction.objects.filter(
                        journal_entry__object_id__in=[
                            *purchase_voucher_row_ids,
                            *debit_note_row_ids,
                        ],
                        journal_entry__content_type__model__in=[
                            "purchasevoucherrow",
                            "debitnoterow",
                        ],
                        account=item.discount_received_account,
                    ).update(account=discount_received_account)

            Item.objects.filter(category=self, company=self.company).update(
                **update_fields
            )

        if "dedicated" in {
            self.items_sales_account_type,
            self.items_discount_allowed_account_type,
            self.items_purchase_account_type,
            self.items_discount_received_account_type,
        }:
            items_list = Item.objects.filter(
                category=self, company=self.company
            ).select_related(
                "sales_account",
                "discount_allowed_account",
                "purchase_account",
                "discount_received_account",
                "dedicated_sales_account",
                "dedicated_discount_allowed_account",
                "dedicated_purchase_account",
                "dedicated_discount_received_account",
            )
            for item in items_list:
                sales_voucher_row_ids = SalesVoucherRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                credit_note_row_ids = CreditNoteRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                purchase_voucher_row_ids = PurchaseVoucherRow.objects.filter(
                    item=item
                ).values_list("id", flat=True)
                debit_note_row_ids = DebitNoteRow.objects.filter(item=item).values_list(
                    "id", flat=True
                )
                acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
                if self.can_be_sold:
                    if self.items_sales_account_type == "dedicated":
                        item.sales_account_type = "dedicated"
                        sales_ledger_transactions = LedgerTransaction.objects.filter(
                            journal_entry__object_id__in=[
                                *sales_voucher_row_ids,
                                *credit_note_row_ids,
                            ],
                            journal_entry__content_type__model__in=[
                                "salesvoucherrow",
                                "creditnoterow",
                            ],
                            account=item.sales_account,
                        )
                        if not item.dedicated_sales_account:
                            sales_account_name = item.name + " (Sales)"
                            account = Account(
                                name=sales_account_name, company=self.company
                            )
                            if self.sales_account_category is not None:
                                account.category = self.sales_account_category
                            else:
                                account.add_category(acc_cat_system_codes["Sales"])
                            account.suggest_code(item)
                            account.save()
                            item.dedicated_sales_account = account
                            item.sales_account = account
                        else:
                            item.sales_account = item.dedicated_sales_account
                        sales_ledger_transactions.update(
                            account=item.dedicated_sales_account
                        )

                    if self.items_discount_allowed_account_type == "dedicated":
                        item.discount_allowed_account_type = "dedicated"
                        discount_allowed_transactions = (
                            LedgerTransaction.objects.filter(
                                journal_entry__object_id__in=[
                                    *sales_voucher_row_ids,
                                    *credit_note_row_ids,
                                ],
                                journal_entry__content_type__model__in=[
                                    "salesvoucherrow",
                                    "creditnoterow",
                                ],
                                account=item.discount_allowed_account,
                            )
                        )
                        if not item.dedicated_discount_allowed_account:
                            discount_allowed_account_name = (
                                "Discount Allowed - " + item.name
                            )
                            account = Account(
                                name=discount_allowed_account_name, company=self.company
                            )
                            if self.discount_allowed_account_category is not None:
                                account.category = (
                                    self.discount_allowed_account_category
                                )
                            else:
                                account.add_category(
                                    acc_cat_system_codes["Discount Expenses"]
                                )
                            account.suggest_code(item)
                            account.save()
                            item.dedicated_discount_allowed_account = account
                            item.discount_allowed_account = account
                        else:
                            item.discount_allowed_account = (
                                item.dedicated_discount_allowed_account
                            )
                        discount_allowed_transactions.update(
                            account=item.dedicated_discount_allowed_account
                        )

                    if self.items_purchase_account_type == "dedicated":
                        item.purchase_account_type = "dedicated"
                        purchase_ledger_transactions = LedgerTransaction.objects.filter(
                            journal_entry__object_id__in=[
                                *purchase_voucher_row_ids,
                                *debit_note_row_ids,
                            ],
                            journal_entry__content_type__model__in=[
                                "purchasevoucherrow",
                                "debitnoterow",
                            ],
                            account=item.purchase_account,
                        )
                        if not item.dedicated_purchase_account:
                            purchase_account_name = item.name + " (Purchase)"
                            account = Account(
                                name=purchase_account_name, company=self.company
                            )
                            if self.purchase_account_category is not None:
                                account.category = self.purchase_account_category
                            else:
                                account.add_category(acc_cat_system_codes["Purchase"])
                            account.suggest_code(item)
                            account.save()
                            item.dedicated_purchase_account = account
                            item.purchase_account = account
                        else:
                            item.purchase_account = item.dedicated_purchase_account
                        purchase_ledger_transactions.update(
                            account=item.dedicated_purchase_account
                        )

                    if self.items_discount_received_account_type == "dedicated":
                        item.discount_received_account_type = "dedicated"
                        discount_received_transactions = (
                            LedgerTransaction.objects.filter(
                                journal_entry__object_id__in=[
                                    *purchase_voucher_row_ids,
                                    *debit_note_row_ids,
                                ],
                                journal_entry__content_type__model__in=[
                                    "purchasevoucherrow",
                                    "debitnoterow",
                                ],
                                account=item.discount_received_account,
                            )
                        )
                        if not item.dedicated_discount_received_account:
                            discount_received_account_name = (
                                "Discount Received - " + item.name
                            )
                            account = Account(
                                name=discount_received_account_name,
                                company=self.company,
                            )
                            if self.discount_received_account_category is not None:
                                account.category = (
                                    self.discount_received_account_category
                                )
                            else:
                                account.add_category(
                                    acc_cat_system_codes["Discount Expenses"]
                                )
                            account.suggest_code(item)
                            account.save()
                            item.dedicated_discount_received_account = account
                            item.discount_received_account = account
                        else:
                            item.discount_received_account = (
                                item.dedicated_discount_received_account
                            )
                        discount_received_transactions.update(
                            account=item.dedicated_discount_received_account
                        )
            # TODO: fileds can be filtered for optimization
            Item.objects.bulk_update(
                items_list,
                [
                    "sales_account",
                    "sales_account_type",
                    "dedicated_sales_account",
                    "discount_allowed_account",
                    "discount_allowed_account_type",
                    "dedicated_discount_allowed_account",
                    "purchase_account",
                    "purchase_account_type",
                    "dedicated_purchase_account",
                    "discount_received_account",
                    "discount_received_account_type",
                    "dedicated_discount_received_account",
                ],
            )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = (
            ("code", "company"),
            ("name", "company"),
        )


class InventoryAccount(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    account_no = models.PositiveIntegerField(blank=True, null=True)
    current_balance = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    opening_balance = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    opening_balance_rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="inventory",
    )

    def __str__(self):
        return self.name

    @staticmethod
    def get_next_account_no():
        from django.db.models import Max

        max_voucher_no = InventoryAccount.objects.all().aggregate(Max("account_no"))[
            "account_no__max"
        ]
        if max_voucher_no:
            return max_voucher_no + 1
        else:
            return 1

    def get_category(self):
        try:
            item = self.item
        except:
            return None
        try:
            category = item.category
        except:
            return None
        return category

    @property
    def amounts(self):
        return Transaction.objects.filter(account=self).aggregate(
            dr=Sum("dr_amount"), cr=Sum("cr_amount")
        )

    def save(self, *args, **kwargs):
        if not self.account_no:
            self.account_no = self.get_next_account_no()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-id"]


class JournalEntry(models.Model):
    date = models.DateField()
    content_type = models.ForeignKey(
        ContentType, related_name="inventory_journal_entries", on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey("content_type", "object_id")
    source_voucher_no = models.CharField(max_length=50, blank=True, null=True)
    source_voucher_id = models.PositiveIntegerField(blank=True, null=True)

    @staticmethod
    def get_for(source):
        try:
            return JournalEntry.objects.get(
                content_type=ContentType.objects.get_for_model(source),
                object_id=source.id,
            )
        except JournalEntry.DoesNotExist:
            return None

    def __str__(self):
        return (
            str(self.content_type)
            + ": "
            + str(self.object_id)
            + " ["
            + str(self.date)
            + "]"
        )

    class Meta:
        verbose_name_plural = "Inventory Journal Entries"


class Transaction(models.Model):
    account = models.ForeignKey(
        InventoryAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    dr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    cr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    current_balance = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    journal_entry = models.ForeignKey(
        JournalEntry, related_name="transactions", on_delete=models.CASCADE
    )
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    remaining_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    fifo_inconsistency_quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )  # This is the quantity that is not accounted for in the fifo, or say which is not consumed
    consumption_data = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return (
            str(self.account)
            + " ["
            + str(self.dr_amount)
            + " / "
            + str(self.cr_amount)
            + "]"
        )

    def total_dr_amount(self):
        dr_transctions = Transaction.objects.filter(
            account__name=self.account.name,
            cr_amount=None,
            journal_entry__journal__rate=self.journal_entry.source.rate,
        )
        total = 0
        for transaction in dr_transctions:
            total += transaction.dr_amount
        return total

    def total_dr_amount_without_rate(self):
        dr_transctions = Transaction.objects.filter(
            account__name=self.account.name, cr_amount=None
        )
        total = 0
        for transaction in dr_transctions:
            total += transaction.dr_amount
        return total

    def get_balance(self):
        return zero_for_none(self.dr_amount) - zero_for_none(self.cr_amount)


def alter(account, date, diff):
    Transaction.objects.filter(journal_entry__date__gt=date, account=account).update(
        current_balance=(
            Coalesce(F("current_balance"), Value(Decimal("0.000000")))
            + Value(zero_for_none(diff))
        )
    )


@receiver(pre_delete, sender=Transaction)
def _transaction_delete(sender, instance, **kwargs):
    transaction = instance
    if transaction.dr_amount:
        transaction.account.current_balance -= transaction.dr_amount

    if transaction.cr_amount:
        transaction.account.current_balance += transaction.cr_amount

    diff = zero_for_none(transaction.dr_amount) - zero_for_none(transaction.cr_amount)
    alter(transaction.account, transaction.journal_entry.date, diff)

    transaction.account.save()


def find_obsolete_transactions(model, date, *args):
    args = [arg for arg in args if arg is not None]

    try:
        journal_entry = JournalEntry.objects.get(
            content_type=ContentType.objects.get_for_model(model), object_id=model.id
        )
    except JournalEntry.DoesNotExist:
        if model.voucher.status not in ["Cancelled", "Draft"]:
            print("Not found", model, model.voucher.status, model.voucher.id)
        return

    all_transaction_ids = []
    for arg in args:
        matches = journal_entry.transactions.filter(account=arg[1])
        if not matches:
            transaction = Transaction()
        else:
            transaction = matches[0]
        all_transaction_ids.append(transaction.id)

    obsolete_transactions = journal_entry.transactions.exclude(
        id__in=all_transaction_ids
    )
    if obsolete_transactions.count():
        print(obsolete_transactions)
        obsolete_transactions.delete()


def fifo_avg(consumption_data, required_quantity):
    # sort consumption data by key
    consumption_data = OrderedDict(
        sorted(consumption_data.items(), key=lambda x: int(x[0]))
    )
    cumulative_quantity = Decimal("0")
    cumulative_rate = Decimal("0")

    # in fifo, we can't consume more than the total quantity
    # if the required quantity is more than the total quantity,
    # we'll calculate the average rate for the total quantity
    required_quantity = min(
        required_quantity, sum([Decimal(x[0]) for x in consumption_data.values()])
    )

    for quantity, rate in consumption_data.values():
        _quantity = Decimal(quantity)
        _rate = Decimal(rate)
        if cumulative_quantity + _quantity <= required_quantity:
            cumulative_quantity += _quantity
            cumulative_rate += _quantity * _rate
        else:
            remaining_quantity = required_quantity - cumulative_quantity
            cumulative_rate += remaining_quantity * _rate
            break
    # TODO: temp fix for 0 required_quantity
    return cumulative_rate / (required_quantity or 1)


def set_inventory_transactions(model, date, *args, clear=True):
    args = [arg for arg in args if arg is not None]

    content_type = ContentType.objects.get_for_model(model)

    created = False
    try:
        journal_entry = JournalEntry.objects.get(
            content_type=content_type, object_id=model.id
        )
    except JournalEntry.DoesNotExist:
        if hasattr(model, "voucher_id"):
            voucher_id = model.voucher_id
            voucher_no = model.voucher.voucher_no
        else:
            voucher_id = model.id
            voucher_no = model.voucher_no

        journal_entry = JournalEntry(
            content_type=content_type,
            object_id=model.id,
            date=date,
            source_voucher_id=voucher_id,
            source_voucher_no=voucher_no,
        )
        journal_entry.save()
        created = True

    all_transaction_ids = []

    for arg in args:
        matches = (
            journal_entry.transactions.filter(account=arg[1]) if not created else []
        )
        diff = 0

        arg[2] = Decimal(arg[2])

        if not matches:
            transaction = Transaction()
        else:
            transaction = matches[0]
            diff = zero_for_none(transaction.cr_amount) - zero_for_none(
                transaction.dr_amount
            )
        if arg[0] in ["dr", "ob"]:
            transaction.cr_amount = None
            transaction.dr_amount = arg[2]
            transaction.remaining_quantity = arg[2]
            diff += arg[2]

            # check if a transaction with later date has been created
            # if yes, then we'll recalculate the fifo for all transactions referencing transaction after this date
            future_dr_transactions = Transaction.objects.filter(
                account=arg[1],
                journal_entry__date__gt=date,
                dr_amount__gt=0,
            ).values_list("id", flat=True)

            future_dr_transactions = list(future_dr_transactions)

            # if the transaction is already created, then we'll add it to the list
            if transaction.id:
                future_dr_transactions.append(transaction.id)

            updated_txns = []

            dr_txns = {
                txn.id: txn
                for txn in Transaction.objects.filter(id__in=future_dr_transactions)
            }

            for txn in Transaction.objects.filter(
                consumption_data__has_any_keys=future_dr_transactions
            ):
                txn.fifo_inconsistency_quantity = zero_for_none(
                    txn.fifo_inconsistency_quantity
                )

                for key, value in list(txn.consumption_data.items()):
                    if dr_txn := dr_txns.get(int(key), None):
                        dr_txn.remaining_quantity += Decimal(value[0])
                        updated_txns.append(dr_txn)
                        txn.fifo_inconsistency_quantity += Decimal(value[0])
                        txn.consumption_data.pop(key)

                updated_txns.append(txn)

            Transaction.objects.bulk_update(
                updated_txns,
                [
                    "fifo_inconsistency_quantity",
                    "consumption_data",
                    "remaining_quantity",
                ],
            )

            # check if the transaction is for Credit Note. If yes, then find the corresponding sales voucher row and transaction
            if content_type.model == "creditnoterow":
                t = Transaction.objects.get(
                    journal_entry__object_id=model.sales_row_data["id"],
                    journal_entry__content_type__model="salesvoucherrow",
                )
                arg[3] = fifo_avg(t.consumption_data, arg[2])

        elif arg[0] == "cr":
            transaction.consumption_data = transaction.consumption_data or {}
            transaction.cr_amount = arg[2]
            transaction.dr_amount = None
            diff -= arg[2]

            # check first if the transaction is for Debit Note, as it requires different handling
            if content_type.model == "debitnoterow":
                # find the corresponding purchase voucher row and transaction

                t = Transaction.objects.get(
                    journal_entry__object_id=model.purchase_row_data["id"],
                    journal_entry__content_type__model="purchasevoucherrow",
                )
                t.remaining_quantity = t.dr_amount - arg[2]
                t.save()

                # here we assume that all transaction referencing this transaction has been affetcted and
                # we'll recalulate the fifo for all of them
                (
                    Transaction.objects.filter(
                        consumption_data__has_key=str(t.id)
                    ).update(
                        fifo_inconsistency_quantity=(
                            Coalesce(F("fifo_inconsistency_quantity"), 0)
                            + Cast(
                                F(f"consumption_data__{t.id}__0"),
                                models.DecimalField(max_digits=24, decimal_places=6),
                            )
                        ),
                        consumption_data=F("consumption_data") - str(t.id),
                    ),
                )

                transaction.consumption_data[t.id] = [
                    str(arg[2]),
                    str(t.rate),
                ]

            else:
                if Transaction.objects.filter(
                    account=arg[1], cr_amount__gt=0, fifo_inconsistency_quantity__gt=0
                ).exists():
                    transaction.fifo_inconsistency_quantity = arg[2]
                else:
                    # check if transaction is for back date; if so, then will have to declare all credit transactions as fifo_inconsistency_quantity, and put the used quantity back to the respective dr transactions
                    future_transactions = Transaction.objects.filter(
                        account=arg[1], journal_entry__date__gt=date, cr_amount__gt=0
                    )

                    dr_ids = (
                        future_transactions.annotate(
                            keys=Func(
                                F("consumption_data"), function="jsonb_object_keys"
                            )
                        )
                        .values_list("keys", flat=True)
                        .distinct()
                    )

                    dr_ids = list(dr_ids)

                    if transaction.id:
                        dr_ids.extend(
                            [
                                key
                                for key in transaction.consumption_data.keys()
                                if key not in dr_ids
                            ]
                        )

                    dr_txns = {
                        txn.id: txn for txn in Transaction.objects.filter(id__in=dr_ids)
                    }

                    updated_txns = []

                    for txn in future_transactions:
                        txn.fifo_inconsistency_quantity = txn.cr_amount
                        for key, value in txn.consumption_data.items():
                            dr_txn = dr_txns[int(key)]
                            dr_txn.remaining_quantity += Decimal(value[0])
                            updated_txns.append(dr_txn)
                        txn.consumption_data = {}
                        updated_txns.append(txn)

                    Transaction.objects.bulk_update(
                        updated_txns,
                        [
                            "fifo_inconsistency_quantity",
                            "consumption_data",
                            "remaining_quantity",
                        ],
                    )

                    # Consumption data
                    req_qty = arg[2]

                    base_txn_qs = (
                        Transaction.objects.filter(
                            account=arg[1], cr_amount=None, remaining_quantity__gt=0
                        )
                        .annotate(
                            running=Window(
                                expression=Sum("remaining_quantity"),
                                order_by=["journal_entry__date", "id"],
                            )
                        )
                        .order_by("journal_entry__date", "id")
                        .only("id", "remaining_quantity")
                    )

                    txn_qs = base_txn_qs.filter(running__lte=req_qty)
                    count = len(txn_qs)
                    if count:
                        updated_txns = []

                        # if the cumulative remaining quantity of the transactions is less than the required quantity fetch the next transaction as well

                        # the last transaction i.e. the one with the highest running (< req_qty)
                        txn_highest = txn_qs[count - 1]

                        if txn_highest.running < req_qty:
                            tx_next = base_txn_qs.filter(running__gt=req_qty).first()
                            req_qty -= txn_highest.running
                            if tx_next:
                                tx_next.remaining_quantity -= req_qty
                                updated_txns.append(tx_next)
                                transaction.consumption_data[tx_next.id] = [
                                    str(req_qty),
                                    str(tx_next.rate),
                                ]
                            else:
                                transaction.fifo_inconsistency_quantity = req_qty

                        for txn in txn_qs:
                            transaction.consumption_data[txn.id] = [
                                str(txn.remaining_quantity),
                                str(txn.rate),
                            ]

                        updated_txns += [
                            txn
                            for txn in txn_qs
                            if not setattr(txn, "remaining_quantity", 0)
                        ]

                        Transaction.objects.bulk_update(
                            updated_txns, ["remaining_quantity"]
                        )

                    else:  # possibly the required quantity is lesser than any cumulative remaining quantity
                        tx_next = base_txn_qs.filter(running__gt=req_qty).first()
                        if tx_next:
                            tx_next.remaining_quantity -= req_qty
                            tx_next.save()
                            transaction.consumption_data[tx_next.id] = [
                                str(req_qty),
                                str(tx_next.rate),
                            ]
                        else:
                            transaction.fifo_inconsistency_quantity = req_qty
        else:
            raise Exception('Transactions can only be either "dr" or "cr".')
        transaction.account = arg[1]
        if isinstance(transaction.account.current_balance, str):
            transaction.account.current_balance = Decimal(
                transaction.account.current_balance
            )
        transaction.account.current_balance += diff
        transaction.current_balance = transaction.account.current_balance
        transaction.rate = arg[3]
        transaction.account.save()
        journal_entry.transactions.add(transaction, bulk=False)
        alter(transaction.account, date, diff)
        all_transaction_ids.append(transaction.id)

    if clear:
        obsolete_transactions = journal_entry.transactions.exclude(
            id__in=all_transaction_ids
        )
        if obsolete_transactions.count():
            obsolete_transactions.delete()


class TransactionRemovalLog(models.Model):
    deleted_at = models.DateTimeField(auto_now_add=True)
    row_id = models.PositiveIntegerField(primary_key=True)
    transaction_type = models.CharField(
        max_length=50,
        choices=[
            ("Ledger", "Ledger"),
            ("Inventory", "Inventory"),
        ],
    )
    row_dump = models.JSONField(null=True, blank=True)


@receiver(pre_delete, sender=Transaction)
def _transaction_delete(sender, instance, **kwargs):
    # if a tarnsaction is deleted, find the transaction which has consumed from this transaction
    # and remove reference from it, and add the quantity to fifo_inconsistency_quantity
    # using the fifo_inconsistency_quantity field, we can find the transactions which
    # have been affected by this transaction and recalculate the fifo

    if instance.dr_amount:
        Transaction.objects.filter(consumption_data__has_key=str(instance.id)).update(
            fifo_inconsistency_quantity=(
                Coalesce(F("fifo_inconsistency_quantity"), 0)
                + Cast(
                    F(f"consumption_data__{instance.id}__0"),
                    models.DecimalField(max_digits=24, decimal_places=6),
                )
            ),
            consumption_data=F("consumption_data") - str(instance.id),
        )

    if instance.cr_amount:
        later_transactions = Transaction.objects.filter(
            account=instance.account,
            journal_entry__date__gte=instance.journal_entry.date,
            id__gte=instance.id,
            cr_amount__gt=0,
        )

        dr_ids = (
            later_transactions.annotate(
                keys=Func(F("consumption_data"), function="jsonb_object_keys")
            )
            .values_list("keys", flat=True)
            .distinct()
        )

        dr_txns = {
            txn.id: txn for txn in Transaction.objects.filter(id__in=list(dr_ids))
        }

        updated_txns = []

        for txn in later_transactions:
            txn.fifo_inconsistency_quantity = txn.cr_amount
            for key, value in txn.consumption_data.items():
                dr_txn = dr_txns[int(key)]
                dr_txn.remaining_quantity += value[0]
                updated_txns.append(dr_txn)
            txn.consumption_data = {}
            if txn.id != instance.id:
                updated_txns.append(txn)

        Transaction.objects.bulk_update(
            updated_txns,
            [
                "fifo_inconsistency_quantity",
                "consumption_data",
                "remaining_quantity",
            ],
        )

    TransactionRemovalLog.objects.create(
        row_id=instance.id,
        transaction_type="Inventory",
        row_dump=jsonify(instance),
    )


class Item(CompanyBaseModel):
    ACCOUNT_TYPE_CHOICES = [
        ("global", "Global"),
        ("dedicated", "Dedicated"),
        ("category", "Category"),
        ("existing", "Existing"),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    voucher_no = models.PositiveBigIntegerField(null=True, blank=True)
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        related_name="items",
        on_delete=models.SET_NULL,
    )
    description = models.TextField(blank=True, null=True)
    selling_price = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    cost_price = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    front_image = models.ImageField(
        blank=True, null=True, upload_to="item_front_images/"
    )
    back_image = models.ImageField(blank=True, null=True, upload_to="item_back_images/")

    brand = models.ForeignKey(
        Brand, blank=True, null=True, related_name="items", on_delete=models.SET_NULL
    )

    tax_scheme = models.ForeignKey(
        TaxScheme,
        blank=True,
        null=True,
        related_name="items",
        on_delete=models.SET_NULL,
    )

    account = models.OneToOneField(
        InventoryAccount, related_name="item", null=True, on_delete=models.CASCADE
    )

    sales_account = models.ForeignKey(
        Account, null=True, on_delete=models.SET_NULL, related_name="sales_item"
    )
    sales_account_type = models.CharField(
        max_length=16, null=True, blank=True, choices=ACCOUNT_TYPE_CHOICES
    )
    dedicated_sales_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sales_item_dedicated",
    )

    purchase_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_item",
    )
    purchase_account_type = models.CharField(
        max_length=16, null=True, blank=True, choices=ACCOUNT_TYPE_CHOICES
    )
    dedicated_purchase_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="purchase_item_dedicated",
    )

    discount_allowed_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_allowed_item",
    )
    discount_allowed_account_type = models.CharField(
        max_length=16, null=True, blank=True, choices=ACCOUNT_TYPE_CHOICES
    )
    dedicated_discount_allowed_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_allowed_item_dedicated",
    )

    discount_received_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_received_item",
    )
    discount_received_account_type = models.CharField(
        max_length=16, null=True, blank=True, choices=ACCOUNT_TYPE_CHOICES
    )
    dedicated_discount_received_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="discount_received_item_dedicated",
    )

    expense_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="expense_item",
    )
    fixed_asset_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="fixed_asset_item",
    )

    track_inventory = models.BooleanField(default=True)
    can_be_sold = models.BooleanField(default=True)
    can_be_purchased = models.BooleanField(default=True)
    fixed_asset = models.BooleanField(default=False)
    direct_expense = models.BooleanField(default=False)
    indirect_expense = models.BooleanField(default=False)

    extra_data = JSONField(null=True, blank=True, default=dict)
    search_data = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, related_name="items", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def expense(self):
        return self.direct_expense or self.indirect_expense

    @property
    def is_trackable(self):
        return self.track_inventory or self.fixed_asset

    @property
    def dr_account(self):
        if self.expense:
            return self.expense_account
        if self.fixed_asset:
            return self.fixed_asset_account
        return self.purchase_account
    
    def get_or_create_capital_expense_account(self):
        """
        Returns the capital expense account for the given item.
        If it does not exist, it creates a new one.
        """
        company = self.company
        capex_system_code = acc_cat_system_codes.get("Capital Expenses")
        assets_system_code = acc_cat_system_codes.get("Assets")

        capital_expense_category, _ = AccountCategory.objects.get_or_create(
            company=company,
            system_code=capex_system_code,
            defaults={
                "name": "Capital Expenses",
                "parent": AccountCategory.objects.get(
                    system_code=assets_system_code,
                    company=company
                ),
                "code": "CAP-EX",
                "default": True,
            }
        )

        system_code = f"CE-I:{self.pk}"
        capital_expense_account, _ = Account.objects.get_or_create(
            company=company,
            system_code=system_code,
            defaults={
                "name": self.name,
                "category": capital_expense_category,
                "code": "CAP-EX",
                "default": True,
            }
        )
        return capital_expense_account

    def update_opening_balance(self, fiscal_year):
        date = fiscal_year.previous_day
        set_inventory_transactions(
            self,
            date,
            [
                "dr",
                self.account,
                self.account.opening_balance,
                self.account.opening_balance_rate,
            ],
        )

    def get_source_id(self):
        # Used as transaction source for opening balance
        return self.id

    def save(self, *args, **kwargs):
        self.validate_unique()

        post_save = kwargs.pop("post_save", True)
        super().save(*args, **kwargs)

        if post_save:
            if not self.voucher_no:
                self.voucher_no = self.pk

            sales_account_name = self.name + " (Sales)"
            discount_allowed_account_name = "Discount Allowed - " + self.name
            purchase_account_name = self.name + " (Purchase)"
            discount_received_account_name = "Discount Received - " + self.name
            if not self.voucher_no:
                self.voucher_no = self.pk

            # Update dedicated accounts
            if self.dedicated_sales_account:
                if not self.dedicated_sales_account.name == sales_account_name:
                    self.dedicated_sales_account.name = sales_account_name
                    self.dedicated_sales_account.save()

            if self.dedicated_purchase_account:
                if not self.dedicated_purchase_account.name == purchase_account_name:
                    self.dedicated_purchase_account.name = purchase_account_name
                    self.dedicated_purchase_account.save()

            if self.dedicated_discount_allowed_account:
                if (
                    not self.dedicated_discount_allowed_account.name
                    == discount_allowed_account_name
                ):
                    self.dedicated_discount_allowed_account.name = (
                        discount_allowed_account_name
                    )
                    self.dedicated_discount_allowed_account.save()

            if self.dedicated_discount_received_account:
                if (
                    not self.dedicated_discount_received_account.name
                    == discount_received_account_name
                ):
                    self.dedicated_discount_received_account.name = (
                        discount_received_account_name
                    )
                    self.dedicated_discount_received_account.save()

            acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
            if self.can_be_sold:
                if not self.sales_account_id:
                    if not self.dedicated_sales_account:
                        account = Account(name=sales_account_name, company=self.company)
                        if self.category and self.category.sales_account_category_id:
                            account.category = self.category.sales_account_category
                        else:
                            account.add_category(acc_cat_system_codes["Sales"])
                        account.suggest_code(self)
                        account.save()
                        self.dedicated_sales_account = account
                        self.sales_account_type = "dedicated"
                    else:
                        account = self.dedicated_sales_account
                    self.sales_account = account

                if not self.discount_allowed_account_id:
                    if not self.dedicated_discount_allowed_account:
                        discount_allowed_account = Account(
                            name=discount_allowed_account_name, company=self.company
                        )
                        if (
                            self.category
                            and self.category.discount_allowed_account_category_id
                        ):
                            discount_allowed_account.category = (
                                self.category.discount_allowed_account_category
                            )
                        else:
                            discount_allowed_account.add_category(
                                acc_cat_system_codes["Discount Expenses"]
                            )
                        discount_allowed_account.suggest_code(self)
                        discount_allowed_account.save()
                        self.dedicated_discount_allowed_account = (
                            discount_allowed_account
                        )
                        self.discount_allowed_account_type = "dedicated"
                    else:
                        discount_allowed_account = (
                            self.dedicated_discount_allowed_account
                        )
                    self.discount_allowed_account = discount_allowed_account

            if self.can_be_purchased:
                if not self.purchase_account_id:
                    if not self.dedicated_purchase_account:
                        account = Account(
                            name=purchase_account_name, company=self.company
                        )
                        if self.category and self.category.purchase_account_category_id:
                            account.category = self.category.purchase_account_category
                        else:
                            account.add_category(acc_cat_system_codes["Purchase"])
                        account.suggest_code(self)
                        account.save()
                        self.dedicated_purchase_account = account
                        self.purchase_account_type = "dedicated"
                    else:
                        account = self.dedicated_purchase_account
                    self.purchase_account = account

            if self.can_be_purchased or self.fixed_asset or self.expense:
                if not self.discount_received_account_id:
                    if not self.dedicated_discount_received_account:
                        discount_received_acc = Account(
                            name=discount_received_account_name, company=self.company
                        )
                        if (
                            self.category
                            and self.category.discount_received_account_category_id
                        ):
                            discount_received_acc.category = (
                                self.category.discount_received_account_category
                            )
                        else:
                            discount_received_acc.add_category(
                                acc_cat_system_codes["Discount Income"]
                            )
                        discount_received_acc.suggest_code(self)
                        discount_received_acc.save()
                        self.dedicated_discount_received_account = discount_received_acc
                        self.discount_received_account_type = "dedicated"
                    else:
                        discount_received_acc = self.dedicated_discount_received_account
                    self.discount_received_account = discount_received_acc

            if self.direct_expense or self.indirect_expense:
                if not self.expense_account_id:
                    expense_account = Account(name=self.name, company=self.company)
                    if self.direct_expense:
                        if (
                            self.category
                            and self.category.direct_expense_account_category_id
                        ):
                            expense_account.category = (
                                self.category.direct_expense_account_category
                            )
                        else:
                            expense_account.add_category(
                                acc_cat_system_codes["Direct Expenses"]
                            )
                    else:
                        if (
                            self.category
                            and self.category.indirect_expense_account_category_id
                        ):
                            expense_account.category = (
                                self.category.indirect_expense_account_category
                            )
                        else:
                            expense_account.add_category(
                                acc_cat_system_codes["Indirect Expenses"]
                            )
                    expense_account.suggest_code(self)
                    expense_account.save()
                    self.expense_account = expense_account
                elif self.expense_account.name != self.name:
                    self.expense_account.name = self.name
                    self.expense_account.save()

            if self.fixed_asset:
                if not self.fixed_asset_account_id:
                    fixed_asset_account = Account(name=self.name, company=self.company)
                    if self.category and self.category.fixed_asset_account_category_id:
                        fixed_asset_account.category = (
                            self.category.fixed_asset_account_category
                        )
                    else:
                        fixed_asset_account.add_category(
                            acc_cat_system_codes["Fixed Assets"]
                        )
                    fixed_asset_account.suggest_code(self)
                    fixed_asset_account.save()
                    self.fixed_asset_account = fixed_asset_account
                elif self.fixed_asset_account.name != self.name:
                    self.fixed_asset_account.name = self.name
                    self.fixed_asset_account.save()

            if self.track_inventory or self.fixed_asset:
                if not self.account_id:
                    account = InventoryAccount(
                        code=self.code, name=self.name, company_id=self.company_id
                    )
                    account.save()
                    self.account = account
                elif self.account.name != self.name:
                    self.account.name = self.name
                    self.account.save()

            if self.category and self.category.extra_fields:
                search_data = []
                for field in self.category.extra_fields:
                    if type(field) in [dict, OrderedDict]:
                        if field.get("enable_search"):
                            if type(self.extra_data) in [dict, OrderedDict]:
                                search_data.append(
                                    str(self.extra_data.get(field.get("name")))
                                )

                search_text = ", ".join(search_data)
                self.search_data = search_text

            if self.category:
                # TODO: Why is this required???
                # this triggers account category update
                self.category.save()
            else:
                if (
                    self.sales_account
                    and self.sales_account.category.system_code
                    != acc_cat_system_codes["Sales"]
                ):
                    self.sales_account.add_category("Sales")
                    self.sales_account.save()
                if (
                    self.discount_allowed_account
                    and self.discount_allowed_account.category.system_code
                    != acc_cat_system_codes["Discount Expenses"]
                ):
                    self.discount_allowed_account.add_category(
                        acc_cat_system_codes["Discount Expenses"]
                    )
                    self.discount_allowed_account.save()
                if (
                    self.purchase_account
                    and self.purchase_account.category.system_code
                    != acc_cat_system_codes["Purchase"]
                ):
                    self.purchase_account.add_category(acc_cat_system_codes["Purchase"])
                    self.purchase_account.save()
                if (
                    self.discount_received_account
                    and self.discount_received_account.category.system_code
                    != acc_cat_system_codes["Discount Income"]
                ):
                    self.discount_received_account.add_category(
                        acc_cat_system_codes["Discount Income"]
                    )
                    self.discount_received_account.save()
                if (
                    self.expense_account
                    and self.direct_expense
                    and self.expense_account.category.system_code
                    != acc_cat_system_codes["Direct Expenses"]
                ):
                    self.expense_account.add_category(
                        acc_cat_system_codes["Direct Expenses"]
                    )
                    self.expense_account.save()
                if (
                    self.expense_account
                    and self.indirect_expense
                    and self.expense_account.category.system_code
                    != acc_cat_system_codes["Indirect Expenses"]
                ):
                    self.expense_account.add_category(
                        acc_cat_system_codes["Indirect Expenses"]
                    )
                    self.expense_account.save()
                if (
                    self.fixed_asset
                    and self.fixed_asset_account.category.system_code
                    != acc_cat_system_codes["Fixed Assets"]
                ):
                    self.fixed_asset_account.add_category(
                        acc_cat_system_codes["Fixed Assets"]
                    )
                    self.fixed_asset_account.save()

            # prevents recursion
            self.save(post_save=False)

    # TODO: Why make a new property for this?
    @property
    def remaining_stock(self):
        return self.account.current_balance

    @property
    def available_stock_data(self):
        qs = (
            self.account.transactions.filter(remaining_quantity__gt=0)
            .order_by("journal_entry__date", "id")
            .values("remaining_quantity", "rate")
        )
        return list(qs)

    class Meta:
        unique_together = (
            (
                "code",
                "company",
            ),
        )


class InventorySetting(models.Model):
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="inventory_setting"
    )

    enable_fifo = models.BooleanField(default=False)
    enable_negative_stock_check = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "Inventory Setting - {}".format(self.company.name)


class BillOfMaterial(CompanyBaseModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="bill_of_material"
    )
    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    finished_product = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="bill_of_material"
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.finished_product.name


class BillOfMaterialRow(CompanyBaseModel):
    bill_of_material = models.ForeignKey(
        BillOfMaterial, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "Bill of Material Row - {}".format(self.item.name)


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


class InventoryAdjustmentVoucher(TransactionModel, InvoiceModel):
    voucher_no = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateField()
    issue_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=225, choices=ADJUSTMENT_STATUS_CHOICES)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="inventory_adjustment_voucher"
    )
    purpose = models.CharField(max_length=225, choices=PURPOSE_CHOICES)
    remarks = models.TextField()
    total_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
        null=True,
        blank=True,
    )

    def apply_inventory_transactions(self):
        for row in self.rows.filter(
            Q(item__track_inventory=True) | Q(item__fixed_asset=True)
        ):
            quantity = int(row.quantity)
            if self.purpose == "Stock In":
                transaction_type = "dr"
            else:
                transaction_type = "cr"
            set_inventory_transactions(
                row,
                self.date,
                [transaction_type, row.item.account, quantity, row.rate],
            )

    def apply_transactions(self, voucher_meta=None):
        if self.status == "Cancelled":
            self.cancel_transactions()
            return

        # filter bypasses rows cached by prefetching
        if self.purpose in ["Damaged", "Expired"]:
            for row in self.rows.filter().select_related(
                "item__purchase_account",
            ):
                row_amount = row.quantity * row.rate
                entries = [["cr", row.item.purchase_account, row_amount]]
                acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
                if self.purpose == "Damaged":
                    # TODO: Do not fetch account with name
                    entries.append(
                        [
                            "dr",
                            get_account(
                                self.company, acc_system_codes["Damage Expense"]
                            ),
                            row_amount,
                        ]
                    )
                elif self.purpose == "Expired":
                    entries.append(
                        [
                            "dr",
                            get_account(
                                self.company, acc_system_codes["Expiry Expense"]
                            ),
                            row_amount,
                        ]
                    )
                set_ledger_transactions(row, self.date, *entries, clear=True)

        self.apply_inventory_transactions()


class InventoryAdjustmentVoucherRow(
    TransactionModel,
    InvoiceRowModel,
    CompanyBaseModel,
):
    voucher = models.ForeignKey(
        InventoryAdjustmentVoucher, on_delete=models.CASCADE, related_name="rows"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="inventory_adjustment_rows"
    )
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    unit = models.ForeignKey(
        Unit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField(blank=True, null=True)


class InventoryConversionVoucher(
    TransactionModel,
    InvoiceModel,
    CompanyBaseModel,
):
    voucher_no = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateField()
    finished_product = models.ForeignKey(
        BillOfMaterial,
        null=True,
        blank=True,
        related_name="inventory_conversion_voucher",
        on_delete=models.SET_NULL,
    )
    issue_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=225, choices=CONVERSION_CHOICES)
    company = models.ForeignKey(
        Company,
        related_name="inventory_conversion_voucher",
        on_delete=models.CASCADE,
    )
    remarks = models.TextField()

    def apply_inventory_transactions(self):
        for row in self.rows.filter(Q(item__track_inventory=True)):
            quantity = int(row.quantity)
            set_inventory_transactions(
                row,
                self.date,
                [row.transaction_type.lower(), row.item.account, quantity, row.rate],
            )


class InventoryConversionVoucherRow(
    TransactionModel,
    InvoiceRowModel,
    CompanyBaseModel,
):
    voucher = models.ForeignKey(
        InventoryConversionVoucher,
        related_name="rows",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        Item,
        related_name="inventory_conversion_voucher_rows",
        on_delete=models.CASCADE,
    )
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    unit = models.ForeignKey(
        Unit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    transaction_type = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        choices=TRANSACTION_TYPE_CHOICES,
    )


auditlog.register(InventoryAdjustmentVoucher)
auditlog.register(InventoryAdjustmentVoucherRow)
auditlog.register(InventoryConversionVoucher)
auditlog.register(InventoryConversionVoucherRow)
