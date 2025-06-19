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
        from apps.ledger.models import Category, Account
        root = {}
        for category in Category.ROOT:
            root[category[0]], _ = Category.objects.get_or_create(
                system_code=acc_cat_system_codes[category[0]],
                company=self,
                defaults={
                    'name': category[0],
                    'code': category[1],
                    'default': True,
                }
            )
        

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR EQUITY
        # ================================================

        Account.objects.get_or_create(
            system_code=acc_system_codes["Profit and Loss Account"],
            company=self,
            defaults={
                'name': "Profit and Loss Account",
                'category': root["Equity"],
                'code': "Q-PL",
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="Q-OBE",
            company=self,
            defaults={
                'name': "Opening Balance Equity",
                'category': root["Equity"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="Q-CI",
            company=self,
            defaults={
                'name': "Capital Investment",
                'category': root["Equity"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="Q-DC",
            company=self,
            defaults={
                'name': "Drawing Capital",
                'category': root["Equity"],
                'default': True,
            }
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR ASSETS
        # ================================================

        Category.objects.get_or_create(
            code="A-OR",
            company=self,
            defaults={
                'name': "Other Receivables",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="A-DA",
            company=self,
            defaults={
                'name': "Deferred Assets",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Fixed Assets"],
            company=self,
            defaults={
                'name': "Fixed Assets",
                'code': "A-FA",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="A-LA",
            company=self,
            defaults={
                'name': "Loans and Advances Given",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="A-D",
            company=self,
            defaults={
                'name': "Deposits Made",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="A-E",
            company=self,
            defaults={
                'name': "Employee",
                'parent': root["Assets"],
                'default': True,
            }
        )
        tax_receivables, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Tax Receivables"],
            company=self,
            defaults={
                'name': "Tax Receivables",
                'code': "A-TR",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            system_code=acc_system_codes["TDS Receivables"],
            company=self,
            defaults={
                'name': "TDS Receivables",
                'category': tax_receivables,
                'code': "A-TR-TDS",
                'default': True,
            }
        )

        cash_account_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Cash Accounts"],
            company=self,
            defaults={
                'name': "Cash Accounts",
                'code': "A-C",
                'parent': root["Assets"],
                'default': True,
            }
        )
        cash_account, _ = Account.objects.get_or_create(
            system_code=acc_system_codes["Cash"],
            company=self,
            defaults={
                'name': "Cash",
                'category': cash_account_category,
                'code': "A-C-C",
                'default': True,
            }
        )

        from apps.voucher.models import PaymentMode
        PaymentMode.objects.get_or_create(name="Cash", company=self, defaults={'account': cash_account})
        Category.objects.get_or_create(
            code="A-CE",
            company=self,
            defaults={
                'name': "Cash Equivalent Account",
                'parent': root["Assets"],
                'default': True,
            }
        )

        Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Bank Accounts"],
            company=self,
            defaults={
                'name': "Bank Accounts",
                'code': "A-B",
                'parent': root["Assets"],
                'default': True,
            }
        )

        account_receivables, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Account Receivables"],
            company=self,
            defaults={
                'name': "Account Receivables",
                'code': "A-AR",
                'parent': root["Assets"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Customers"],
            company=self,
            defaults={
                'name': "Customers",
                'code': "A-AR-C",
                'parent': account_receivables,
                'default': True,
            }
        )

        Category.objects.get_or_create(
            code="A-ED",
            company=self,
            defaults={
                'name': "Employee Deductions",
                'parent': root["Assets"],
                'default': True,
            }
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR LIABILITIES
        # =====================================================

        account_payables, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Account Payables"],
            company=self,
            defaults={
                'name': "Account Payables",
                'code': "L-AP",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Suppliers"],
            company=self,
            defaults={
                'name': "Suppliers",
                'parent': account_payables,
                'code': "L-AP-S",
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-OP",
            company=self,
            defaults={
                'name': "Other Payables",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-P",
            company=self,
            defaults={
                'name': "Provisions",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-SL",
            company=self,
            defaults={
                'name': "Secured Loans",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-US",
            company=self,
            defaults={
                'name': "Unsecured Loans",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-DT",
            company=self,
            defaults={
                'name': "Deposits Taken",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="L-LA",
            company=self,
            defaults={
                'name': "Loans & Advances Taken",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-DEP",
            company=self,
            defaults={
                'name': "Provision for Accumulated Depreciation",
                'category': root["Liabilities"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-AFP",
            company=self,
            defaults={
                'name': "Audit Fee Payable",
                'category': root["Liabilities"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-OP",
            company=self,
            defaults={
                'name': "Other Payables",
                'category': root["Liabilities"],
                'default': True,
            }
        )
        duties_and_taxes, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Duties & Taxes"],
            company=self,
            defaults={
                'name': "Duties & Taxes",
                'code': "L-T",
                'parent': root["Liabilities"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-T-I",
            company=self,
            defaults={
                'name': "Income Tax",
                'category': duties_and_taxes,
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-T-TA",
            company=self,
            defaults={
                'name': "TDS (Audit Fee)",
                'category': duties_and_taxes,
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="L-T-TR",
            company=self,
            defaults={
                'name': "TDS (Rent)",
                'category': duties_and_taxes,
                'default': True,
            }
        )

        # CREATE DEFAULT CATEGORIES FOR INCOME
        # =====================================

        sales_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Sales"],
            company=self,
            defaults={
                'name': "Sales",
                'code': "I-S",
                'parent': root["Income"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            system_code=acc_system_codes["Sales Account"],
            company=self,
            defaults={
                'name': "Sales Account",
                'code': "I-S-S",
                'category': sales_category,
                'default': True,
            }
        )
        direct_income, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Direct Income"],
            company=self,
            defaults={
                'name': "Direct Income",
                'parent': root["Income"],
                'code': "I-D",
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="I-D-TR",
            company=self,
            defaults={
                'name': "Transfer and Remittance",
                'parent': direct_income,
                'default': True,
            }
        )
        indirect_income, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Indirect Income"],
            company=self,
            defaults={
                'name': "Indirect Income",
                'parent': root["Income"],
                'code': "I-I",
                'default': True,
            }
        )

        discount_income_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Discount Income"],
            company=self,
            defaults={
                'name': "Discount Income",
                'code': "I-I-DI",
                'parent': indirect_income,
                'default': True,
            }
        )
        Account.objects.get_or_create(
            system_code=acc_system_codes["Discount Income"],
            company=self,
            defaults={
                'name': "Discount Income",
                'code': "I-I-DI-DI",
                'category': discount_income_category,
                'default': True,
            }
        )

        # CREATE DEFAULT CATEGORIES FOR EXPENSES
        # =====================================

        purchase_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Purchase"],
            company=self,
            defaults={
                'name': "Purchase",
                'code': "E-P",
                'parent': root["Expenses"],
                'default': True,
            }
        )
        Account.objects.get_or_create(
            system_code=acc_system_codes["Purchase Account"],
            company=self,
            defaults={
                'name': "Purchase Account",
                'code': "E-P-P",
                'category': purchase_category,
                'default': True,
            }
        )

        direct_expenses, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Direct Expenses"],
            company=self,
            defaults={
                'name': "Direct Expenses",
                'code': "E-D",
                'parent': root["Expenses"],
                'default': True,
            }
        )

        additional_cost_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Additional Cost"],
            company=self,
            defaults={
                'name': "Additional Cost",
                'code': "E-D-AC",
                'parent': direct_expenses,
                'default': True,
            }
        )

        new_additional_cost_accounts = {}

        from apps.voucher.models import LandedCostRowType

        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                account, created = Account.objects.get_or_create(
                    system_code=f"E-D-LC-{cost_type[:3].upper()}{index}",
                    company=self,
                    defaults={
                        'name': cost_type,
                        'category': additional_cost_category,
                        'code': f"E-D-LC-{cost_type[:3].upper()}{index}",
                        'default': True,
                    }
                )
                if created:
                    new_additional_cost_accounts[cost_type] = account.id

        from apps.voucher.models.voucher_settings import PurchaseSetting
        purchase_setting, created = PurchaseSetting.objects.get_or_create(company=self)

        if created:
            purchase_setting.landed_cost_accounts = new_additional_cost_accounts
        else:
            purchase_setting.landed_cost_accounts.update(new_additional_cost_accounts)
        purchase_setting.save()

        Category.objects.get_or_create(
            code="E-D-PE",
            company=self,
            defaults={
                'name': "Purchase Expenses",
                'parent': direct_expenses,
                'default': True,
            }
        )
        indirect_expenses, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Indirect Expenses"],
            company=self,
            defaults={
                'name': "Indirect Expenses",
                'code': "E-I",
                'parent': root["Expenses"],
                'default': True,
            }
        )

        bank_charges, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Bank Charges"],
            company=self,
            defaults={
                'name': "Bank Charges",
                'code': "E-I-BC",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="E-I-BC-BC",
            company=self,
            defaults={
                'name': "Bank Charges",
                'category': bank_charges,
                'default': True,
            }
        )
        Account.objects.get_or_create(
            code="E-I-FP",
            company=self,
            defaults={
                'name': "Fines & Penalties",
                'category': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-P",
            company=self,
            defaults={
                'name': "Pay Head",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-FB",
            company=self,
            defaults={
                'name': "Food and Beverages",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-C",
            company=self,
            defaults={
                'name': "Communication Expenses",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-CC",
            company=self,
            defaults={
                'name': "Courier Charges",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-PS",
            company=self,
            defaults={
                'name': "Printing and Stationery",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-RM",
            company=self,
            defaults={
                'name': "Repair and Maintenance",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        Category.objects.get_or_create(
            code="E-I-FT",
            company=self,
            defaults={
                'name': "Fuel and Transport",
                'parent': indirect_expenses,
                'default': True,
            }
        )
        discount_expense_category, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Discount Expenses"],
            company=self,
            defaults={
                'name': "Discount Expenses",
                'parent': indirect_expenses,
                'code': "E-I-DE",
                'default': True,
            }
        )
        Account.objects.get_or_create(
            system_code=acc_system_codes["Discount Expenses"],
            company=self,
            defaults={
                'name': "Discount Expenses",
                'category': discount_expense_category,
                'code': "E-I-DE-DE",
                'default': True,
            }
        )

        # Opening Balance Difference
        # ==========================

        Account.objects.get_or_create(
            system_code=acc_system_codes["Opening Balance Difference"],
            company=self,
            defaults={
                'name': "Opening Balance Difference",
                'code': "O-OBD",
                'category': root["Opening Balance Difference"],
                'default': True,
            }
        )

        # For Inventory Adjustemnt
        # ==========================
        inventory_write_off_account, _ = Category.objects.get_or_create(
            system_code=acc_cat_system_codes["Inventory Write-off"],
            company=self,
            defaults={
                'name': "Inventory write-off",
                'parent': indirect_expenses,
                'code': "E-I-DE-IWO",
                'default': True,
            }
        )

        Account.objects.get_or_create(
            system_code=acc_system_codes["Damage Expense"],
            company=self,
            defaults={
                'name': "Damage Expense",
                'code': "E-I-DE-IWO-DE",
                'category': inventory_write_off_account,
                'default': True,
            }
        )

        Account.objects.get_or_create(
            system_code=acc_system_codes["Expiry Expense"],
            company=self,
            defaults={
                'name': "Expiry Expense",
                'code': "E-I-DE-IWO-EE",
                'category': inventory_write_off_account,
                'default': True,
            }
        )

        # create default permission for company
        Permission.objects.get_or_create(
            company=self,
            name="Default",
        )

        #  create default settings for company
        from apps.voucher.models.voucher_settings import SalesSetting
        SalesSetting.objects.get_or_create(company=self)
        from apps.quotation.models import QuotationSetting
        QuotationSetting.objects.get_or_create(
            company=self,
            defaults={
                'body_text': "We are pleased to provide you with the following quotation for the listed items.",
                'footer_text': "<div>Terms and conditions apply.</div><div>We look forward to working with you.</div>",
            }
        )
        from apps.product.models import InventorySetting
        InventorySetting.objects.get_or_create(company=self)








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