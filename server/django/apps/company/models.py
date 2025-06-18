import json
import re
import uuid
import warnings
from datetime import timedelta
from functools import cached_property
from typing import Dict

from django.apps import apps
from django.conf import settings
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from apps.company.constants import RESTRICTED_COMPANY_SLUGS
from lib.models import BaseModel
from lib.models.mixins import TimeAuditModel
from lib.string import to_snake

acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES

def get_default_permissions() -> Dict[str, Dict[str, bool]]:
    """
    Dynamically generate default permissions for Django models.

    For models with PermissionsMeta:
    - Uses the defined key (or model name if not specified)
    - Uses the defined actions list/dict

    For models without PermissionsMeta:
    - Uses the model name as key
    - Sets all CRUD operations (read, create, update, delete) to True

    Example with PermissionsMeta:
    ```python
    class UserModel(models.Model):
        class PermissionsMeta:
            key = 'user' # Optional, defaults to to_snake(model.__name__)
            exclude = True # Optional, defaults to False (exclude the model from the permissions)
            actions = ['read', 'create', 'update', 'delete', 'custom_action'] # Required
            # or, actions = {'read': True, 'create': True, ...}
            # or, actions = ['read', 'create', {'update': False}, ...]
    ```

    Returns:
        Dict[str, Dict[str, bool]]: A dictionary mapping model keys to their
        permission configurations.

    Raises:
        ValueError: If the permission configuration is improperly defined.
    """
    DEFAULT_CRUD_ACTIONS = {
        "read": True,
        "create": True,
        "update": True,
        "delete": True,
    }

    ret = {}
    app_models = apps.get_models()
    filtered_models = [
        model
        for model in app_models
        if model._meta.app_label
        in ["api", "company", "ledger", "product", "tax", "voucher"]
    ]

    for model in filtered_models:
        # Get model key - either from PermissionsMeta or model name
        key = to_snake(model.__name__)

        # If model doesn't have PermissionsMeta, set default CRUD permissions
        if not hasattr(model, "PermissionsMeta"):
            ret[key] = DEFAULT_CRUD_ACTIONS.copy()
            continue

        # If model is excluded, skip
        if getattr(model.PermissionsMeta, "exclude", False):
            continue

        # If has PermissionsMeta, get custom key if specified
        key = getattr(model.PermissionsMeta, "key", key)

        # Validate key contains only alphabetical characters and underscores
        if not re.match(r"^[a-z_]+$", key):
            raise ValueError(
                f"PermissionsMeta key for {model.__name__} "
                "can only contain lowercase alphabetical characters and underscores"
                f"Got: {key}"
            )

        # If no actions defined, use default CRUD actions
        if not hasattr(model.PermissionsMeta, "actions"):
            ret[key] = DEFAULT_CRUD_ACTIONS.copy()
            continue

        # Validate and normalize actions
        actions = getattr(model.PermissionsMeta, "actions")

        if not isinstance(actions, (list, dict)):
            raise TypeError(
                f"PermissionsMeta actions for {model.__name__} "
                "must be a list or dictionary"
            )

        if isinstance(actions, list):
            _actions = {}
            for action in actions:
                if isinstance(action, str):
                    _actions[action] = True
                elif isinstance(action, dict) and len(action) == 1:
                    for key, value in action.items():
                        _actions[key] = value
                else:
                    raise TypeError(
                        f"PermissionsMeta actions for {model.__name__} "
                        "must be a list of strings or dictionaries with a single key-value pair"
                    )

            actions = _actions

        ret[key] = actions

    return ret


class FiscalYear(TimeAuditModel):
    name = models.CharField(max_length=24)
    start_date = models.DateField()
    end_date = models.DateField()

    class PermissionsMeta:
        exclude = True

    def __str__(self):
        return self.name

    @property
    def previous_day(self):
        return self.start_date - timedelta(days=1)

    def contains_date(self, date):
        return self.start_date <= date <= self.end_date

    def includes(self, date):
        warnings.warn(
            "FiscalYear.includes() is deprecated, use FiscalYear.contains_date() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.contains_date(date)

    def clean(self):
        super().clean()
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    {"end_date": _("End date must be after start date.")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


def slug_validator(value):
    if value in RESTRICTED_COMPANY_SLUGS:
        raise ValidationError("Slug is not valid")


INVOICE_TEMPLATE_CHOICES = [
    (1, "Template 1"),
    (2, "Template 2"),
    (3, "Template 3"),
    (4, "Template 4")
]


class Company(BaseModel):
    COMPANY_TYPE_CHOICES = [
        ("private_limited", "Private Limited"),
        ("public_limited", "Public Limited"),
        ("sole_proprietorship", "Sole Proprietorship"),
        ("partnership", "Partnership"),
        ("corporation", "Corporation"),
        ("non_profit", "Non-profit"),
    ]

    def get_company_logo_path(self, filename):
        _, ext = filename.split(".")
        filename = f"{uuid.uuid4()}.{ext}"
        return f"{self.slug}/logo/{filename}"

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    name = models.CharField(max_length=255, verbose_name="Company Name")
    logo = models.ImageField(
        verbose_name="Logo",
        blank=True,
        null=True,
        # upload_to=get_company_logo_path,
        upload_to="logos/",
    )
    slug = models.SlugField(
        max_length=48,
        db_index=True,
        unique=True,
        validators=[
            slug_validator,
        ],
    )

    # legal information
    organization_type = models.CharField(
        max_length=255,
        choices=COMPANY_TYPE_CHOICES,
        default=COMPANY_TYPE_CHOICES[0][0],
    )
    tax_identification_number = models.CharField(max_length=255, blank=True, null=True)

    # contact information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    country_iso = models.CharField(max_length=2, blank=True, null=True)
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    postal_code = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=18, blank=True, null=True)
    alternate_phone = models.CharField(max_length=18, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    alternate_email = models.EmailField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)

    # config
    enable_sales_invoice_update = models.BooleanField(default=False)
    enable_cheque_deposit_update = models.BooleanField(default=False)
    enable_credit_note_update = models.BooleanField(default=False)
    enable_debit_note_update = models.BooleanField(default=False)
    enable_sales_agents = models.BooleanField(default=False)
    synchronize_cbms_nepal_test = models.BooleanField(default=False)
    synchronize_cbms_nepal_live = models.BooleanField(default=False)
    config_template = models.CharField(max_length=255, default="np")
    invoice_template = models.IntegerField(choices=INVOICE_TEMPLATE_CHOICES, default=1)

    current_fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.SET_NULL,
        related_name="companies",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ("-id",)
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["name", ""
        #         name="unique_company_slug",
        #     ),
        # ]

    class PermissionsMeta:
        exclude = True

    def __str__(self):
        """Return name of the Company"""
        return self.name

    def _get_company_default_slug(self):
        chunks = self.name.lower().strip().split(" ")
        first_chunk = chunks[0]
        return f"{first_chunk[:38]}-{uuid.uuid4().hex[:9]}"

    def save(self, *args, **kwargs):
        is_creating = self._state.adding

        if is_creating and not self.slug:
            self.slug = self._get_company_default_slug()

        super().save(*args, **kwargs)

        if is_creating:
            self.create_company_defaults()

    def get_fiscal_years(self):
        # TODO Assign fiscal years to companies (m2m), return related fiscal years here
        return sorted(
            FiscalYear.objects.all(),
            key=lambda fy: 999 if fy.id == self.current_fiscal_year_id else fy.id,
            reverse=True,
        )

    def create_company_defaults(self):
        # CREATE ROOT CATEGORIES
        # ================================================
        Category = apps.get_model("ledger", "Category")
        Account = apps.get_model("ledger", "Account")
        root = {}
        for category in Category.ROOT:
            root[category[0]] = Category.objects.create(
                name=category[0],
                code=category[1],
                company=self,
                default=True,
                system_code=acc_cat_system_codes.get(category[0], None),
            )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR EQUITY
        # ================================================

        Account.objects.create(
            name="Profit and Loss Account",
            category=root["Equity"],
            code="Q-PL",
            company=self,
            default=True,
            system_code=acc_system_codes["Profit and Loss Account"],
        )
        Account.objects.create(
            name="Opening Balance Equity",
            category=root["Equity"],
            code="Q-OBE",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Capital Investment",
            category=root["Equity"],
            code="Q-CI",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Drawing Capital",
            category=root["Equity"],
            code="Q-DC",
            company=self,
            default=True,
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR ASSETS
        # ================================================

        Category.objects.create(
            name="Other Receivables",
            code="A-OR",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Deferred Assets",
            code="A-DA",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Fixed Assets",
            code="A-FA",
            parent=root["Assets"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Fixed Assets"],
        )
        Category.objects.create(
            name="Loans and Advances Given",
            code="A-LA",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Deposits Made",
            code="A-D",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Employee",
            code="A-E",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        tax_receivables = Category.objects.create(
            name="Tax Receivables",
            code="A-TR",
            parent=root["Assets"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Tax Receivables"],
        )
        Account.objects.create(
            company=self,
            default=True,
            name="TDS Receivables",
            category=tax_receivables,
            code="A-TR-TDS",
            system_code=acc_system_codes["TDS Receivables"],
        )

        cash_account_category = Category.objects.create(
            name="Cash Accounts",
            code="A-C",
            parent=root["Assets"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Cash Accounts"],
        )
        cash_account = Account.objects.create(
            company=self,
            default=True,
            name="Cash",
            category=cash_account_category,
            code="A-C-C",
            system_code=acc_system_codes["Cash"],
        )

        PaymentMode = apps.get_model("voucher", "PaymentMode")
        PaymentMode.objects.create(name="Cash", account=cash_account, company=self)
        Category.objects.create(
            name="Cash Equivalent Account",
            code="A-CE",
            parent=root["Assets"],
            company=self,
            default=True,
        )

        Category.objects.create(
            name="Bank Accounts",
            code="A-B",
            parent=root["Assets"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Bank Accounts"],
        )

        account_receivables = Category.objects.create(
            name="Account Receivables",
            code="A-AR",
            parent=root["Assets"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Customers",
            code="A-AR-C",
            parent=account_receivables,
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Customers"],
        )

        Category.objects.create(
            name="Employee Deductions",
            code="A-ED",
            parent=root["Assets"],
            company=self,
            default=True,
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR LIABILITIES
        # =====================================================

        account_payables = Category.objects.create(
            name="Account Payables",
            code="L-AP",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Suppliers",
            parent=account_payables,
            code="L-AP-S",
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Suppliers"],
        )
        Category.objects.create(
            name="Other Payables",
            code="L-OP",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Provisions",
            code="L-P",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Secured Loans",
            code="L-SL",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Unsecured Loans",
            code="L-US",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Deposits Taken",
            code="L-DT",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Loans & Advances Taken",
            code="L-LA",
            parent=root["Liabilities"],
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Provision for Accumulated Depreciation",
            category=root["Liabilities"],
            code="L-DEP",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Audit Fee Payable",
            category=root["Liabilities"],
            code="L-AFP",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Other Payables",
            category=root["Liabilities"],
            code="L-OP",
            company=self,
            default=True,
        )
        duties_and_taxes = Category.objects.create(
            name="Duties & Taxes",
            code="L-T",
            parent=root["Liabilities"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Duties & Taxes"],
        )
        Account.objects.create(
            name="Income Tax",
            category=duties_and_taxes,
            code="L-T-I",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="TDS (Audit Fee)",
            category=duties_and_taxes,
            code="L-T-TA",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="TDS (Rent)",
            category=duties_and_taxes,
            code="L-T-TR",
            company=self,
            default=True,
        )

        # CREATE DEFAULT CATEGORIES FOR INCOME
        # =====================================

        sales_category = Category.objects.create(
            name="Sales",
            code="I-S",
            parent=root["Income"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Sales"],
        )
        Account.objects.create(
            name="Sales Account",
            code="I-S-S",
            category=sales_category,
            company=self,
            default=True,
            system_code=acc_system_codes["Sales Account"],
        )
        direct_income = Category.objects.create(
            name="Direct Income",
            code="I-D",
            parent=root["Income"],
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Transfer and Remittance",
            code="I-D-TR",
            parent=direct_income,
            company=self,
            default=True,
        )
        indirect_income = Category.objects.create(
            name="Indirect Income",
            code="I-I",
            parent=root["Income"],
            company=self,
            default=True,
        )

        discount_income_category = Category.objects.create(
            name="Discount Income",
            code="I-I-DI",
            parent=indirect_income,
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Discount Income"],
        )
        Account.objects.create(
            name="Discount Income",
            code="I-I-DI-DI",
            category=discount_income_category,
            company=self,
            default=True,
            system_code=acc_system_codes["Discount Income"],
        )

        # CREATE DEFAULT CATEGORIES FOR EXPENSES
        # =====================================

        purchase_category = Category.objects.create(
            name="Purchase",
            code="E-P",
            parent=root["Expenses"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Purchase"],
        )
        Account.objects.create(
            name="Purchase Account",
            code="E-P-P",
            category=purchase_category,
            company=self,
            default=True,
            system_code=acc_system_codes["Purchase Account"],
        )

        direct_expenses = Category.objects.create(
            name="Direct Expenses",
            code="E-D",
            parent=root["Expenses"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Direct Expenses"],
        )

        additional_cost_category = Category.objects.create(
            name="Additional Cost",
            code="E-D-AC",
            parent=direct_expenses,
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Additional Cost"],
        )

        additional_cost_accounts = {}

        from apps.voucher.models import LandedCostRowType

        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                account = Account.objects.create(
                    name=cost_type,
                    code=f"E-D-LC-{cost_type[:3].upper()}{index}",
                    category=additional_cost_category,
                    company=self,
                    default=True,
                )
                additional_cost_accounts[cost_type] = account.id

        PurchaseSetting = apps.get_model("voucher", "PurchaseSetting")
        purchase_setting, _ = PurchaseSetting.objects.get_or_create(company=self)
        purchase_setting.landed_cost_accounts = additional_cost_accounts
        purchase_setting.save()

        Category.objects.create(
            name="Purchase Expenses",
            code="E-D-PE",
            parent=direct_expenses,
            company=self,
            default=True,
        )
        indirect_expenses = Category.objects.create(
            name="Indirect Expenses",
            code="E-I",
            parent=root["Expenses"],
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Indirect Expenses"],
        )

        bank_charges = Category.objects.create(
            name="Bank Charges",
            code="E-I-BC",
            parent=indirect_expenses,
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Bank Charges"],
        )
        Account.objects.create(
            name="Bank Charges",
            category=bank_charges,
            code="E-I-BC-BC",
            company=self,
            default=True,
        )
        Account.objects.create(
            name="Fines & Penalties",
            category=indirect_expenses,
            code="E-I-FP",
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Pay Head",
            code="E-I-P",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Food and Beverages",
            code="E-I-FB",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Communication Expenses",
            code="E-I-C",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Courier Charges",
            code="E-I-CC",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Printing and Stationery",
            code="E-I-PS",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Repair and Maintenance",
            code="E-I-RM",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        Category.objects.create(
            name="Fuel and Transport",
            code="E-I-FT",
            parent=indirect_expenses,
            company=self,
            default=True,
        )
        discount_expense_category = Category.objects.create(
            name="Discount Expenses",
            parent=indirect_expenses,
            code="E-I-DE",
            company=self,
            default=True,
            system_code=acc_cat_system_codes["Discount Expenses"],
        )
        Account.objects.create(
            name="Discount Expenses",
            category=discount_expense_category,
            code="E-I-DE-DE",
            company=self,
            default=True,
            system_code=acc_system_codes["Discount Expenses"],
        )

        # Opening Balance Difference
        # ==========================

        Account.objects.create(
            name="Opening Balance Difference",
            code="O-OBD",
            category=root["Opening Balance Difference"],
            company=self,
            default=True,
            system_code=acc_system_codes["Opening Balance Difference"],
        )

        # For Inventory Adjustemnt
        # ==========================
        inventory_write_off_account = Category.objects.create(
            name="Inventory write-off",
            parent=indirect_expenses,
            code="E-I-DE-IWO",
            company=self,
            default=True,
        )

        Account.objects.create(
            name="Damage Expense",
            code="E-I-DE-IWO-DE",
            category=inventory_write_off_account,
            company=self,
            default=True,
            system_code=acc_system_codes["Damage Expense"],
        )

        Account.objects.create(
            name="Expiry Expense",
            code="E-I-DE-IWO-EE",
            category=inventory_write_off_account,
            company=self,
            default=True,
            system_code=acc_system_codes["Expiry Expense"],
        )

        # create default permission for company
        Permission.objects.get_or_create(
            company=self,
            name="Default",
        )

        #  create default settings for company
        SalesSetting.objects.create(company=self)
        QuotationSetting.objects.create(
            company=self,
            body_text="We are pleased to provide you with the following quotation for the listed items.",
            footer_text="<div>Terms and conditions apply.</div><div>We look forward to working with you.</div>",
        )
        InventorySetting.objects.create(company=self)








class CompanyBaseModel(BaseModel):
    # TODO: uncomment this for DRY
    # company = models.ForeignKey(
    #     Company,
    #     models.CASCADE,
    #     related_name="company_%(class)s",
    # )

    class Meta:
        abstract = True

    def check_company_references(self, instance):
        """
        Check that all ForeignKey relationships that reference a `Company`
        have the instance's `company` if it exists or all related instances have the same `company`.
        """
        instance_company = getattr(instance, "company", None)

        for field in instance._meta.get_fields():
            if not isinstance(field, models.ForeignKey):
                continue

            related_instance = getattr(instance, field.name, None)

            if not related_instance or hasattr(related_instance, "company") is False:
                continue

            if related_instance.company is None:
                raise SuspiciousOperation(
                    field.name + " does not reference any company."
                )

            if instance_company is None:
                instance_company = related_instance.company
            elif related_instance.company != instance_company:
                raise SuspiciousOperation(
                    field.name + " references a different company."
                )

    def save(self, *args, **kwargs):
        # self.check_company_references(self)
        super().save(*args, **kwargs)


class Permission(BaseModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_permissions",
    )

    name = models.CharField(max_length=80, verbose_name="Permission Name")
    permissions = models.JSONField(default=get_default_permissions)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["company", "name"]
        verbose_name = "Company Permission"
        verbose_name_plural = "Company Permissions"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} <{self.company.name}>"


class CompanyMember(BaseModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"  # owner can do anything
        ADMIN = "admin", "Admin"  # admin can do anything except deleting the company
        MEMBER = "member", "Member"  # need to explicitly manage permissions

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_members",
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_company",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    permissions = models.ManyToManyField(Permission, related_name="member_permission")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["company", "member"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "role"],
                condition=models.Q(
                    role="owner"  # FIXME: Refactor this to use Role.OWNER
                ),
                name="company_unique_owner",
            ),
        ]
        verbose_name = "Company Member"
        verbose_name_plural = "Company Members"
        ordering = ("-created_at",)

    class PermissionsMeta:
        actions = ["view", "create", "modify", "delete"]

    def __str__(self):
        """Return members of the company"""
        return f"{self.member.email} <{self.company.name}>"

    @property
    def is_owner(self):
        """Check if the member has owner role"""
        return self.role == self.Role.OWNER

    @property
    def is_admin(self):
        """Check if the member has admin role"""
        return self.role == self.Role.ADMIN

    @property
    def is_member(self):
        """Check if the member has member role"""
        return self.role == self.Role.MEMBER

    @cached_property
    def permissions_dict(self):
        """Merge permissions from all permission dictionaries"""

        permissions = self.permissions.values_list("permissions", flat=True)

        # Initialize the merged permissions with the first dictionary
        merged = permissions[0] if permissions else {}

        # Iterate through the remaining permission dictionaries
        for perm_dict in permissions[1:]:
            for category, perms in perm_dict.items():
                # If category doesn't exist in merged, add it
                if category not in merged:
                    merged[category] = perms
                    continue

                # Merge permissions for existing category
                for action, value in perms.items():
                    # If the new value is True, override the existing value
                    if value is True:
                        merged[category][action] = True

        return merged

    def clean(self):
        """Validate that there is only one owner per company"""
        if self.role == self.Role.OWNER and not self.pk:
            if CompanyMember.objects.filter(
                company=self.company,
                role_type=self.Role.OWNER,
            ).exists():
                raise ValidationError("Company already has an owner")
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CompanyMemberInvite(BaseModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_memberinvites",
    )
    email = models.CharField(max_length=255)
    accepted = models.BooleanField(default=False)
    responded_at = models.DateTimeField(null=True)
    role = models.CharField(
        max_length=20,
        choices=CompanyMember.Role.choices,
        default=CompanyMember.Role.MEMBER,
    )
    permissions = models.ManyToManyField(Permission, related_name="invite_permission")
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        unique_together = ["email", "company"]
        verbose_name = "Company Member Invite"
        verbose_name_plural = "Company Member Invites"
        ordering = ("-created_at",)

    class PermissionsMeta:
        actions = ["view", "create", "modify", "delete"]

    def __str__(self):
        return f"{self.company.name}-{self.email}-{'Accepted' if self.accepted else 'Pending'}"

    def clean(self):
        if self.role == CompanyMember.Role.OWNER:
            raise ValidationError("Cannot create an owner invite")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_token(self):
        return urlsafe_base64_encode(
            force_bytes(
                json.dumps(
                    {
                        "id": str(self.id),
                        "email": self.email,
                        "company_slug": self.company.slug,
                    }
                )
            )
        )