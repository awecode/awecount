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
        from apps.ledger.models import Category, Account
        from apps.voucher.models import PaymentMode, LandedCostRowType
        from apps.voucher.models.voucher_settings import PurchaseSetting, SalesSetting
        from apps.quotation.models import QuotationSetting
        from apps.product.models import InventorySetting

        # Fetch existing categories and accounts to avoid duplicates
        # Only fetch codes and system_codes that are actually used in the defaults
        used_category_codes = {
            "A", "A-FA", "A-LA", "A-D", "A-E", "A-TR", "A-C", "A-CE", "A-B", "A-AR", "A-AR-C", "A-ED",
            "L-AP", "L-AP-S", "L-OP", "L-P", "L-SL", "L-US", "L-DT", "L-LA", "L-T",
            "I-S", "I-D", "I-D-TR", "I-I", "I-I-DI", "A-OR", "A-DA", "E-D-PE",
            "E-D", "E-I", "E-I-P", "E-I-FB", "E-I-C", "E-I-CC", "E-I-PS", "E-I-RM", "E-I-FT", "E-I-DE", "E-I-DE-IWO"
        }
        used_account_codes = {
            "A-TR-TDS", "A-C-C", "L-DEP", "L-AFP", "L-OP", "L-T-I", "L-T-TA", "L-T-TR",
            "I-S-S", "I-I-DI-DI", "E-I-FP", "E-I-DE-DE", "O-OBD", "E-I-DE-IWO-DE", "E-I-DE-IWO-EE"
        }
        
        existing_categories = {
            cat.code: cat for cat in Category.objects.filter(
                company=self, code__in=used_category_codes
            )
        }
        existing_categories_by_system_code = {
            cat.system_code: cat for cat in Category.objects.filter(
                company=self, system_code__in=acc_cat_system_codes.values()
            )
        }
        existing_accounts = {
            acc.code: acc for acc in Account.objects.filter(
                company=self, code__in=used_account_codes
            )
        }
        # Build system codes for landed cost accounts
        landed_cost_system_codes = []
        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                landed_cost_system_codes.append(system_code)
        
        # Combine regular system codes with landed cost system codes
        all_system_codes = list(acc_system_codes.values()) + landed_cost_system_codes
        
        existing_accounts_by_system_code = {
            acc.system_code: acc for acc in Account.objects.filter(
                company=self, system_code__in=all_system_codes
            )
        }

        # Categories and accounts to be created
        categories_to_create = []
        accounts_to_create = []

        # Helper function to get or prepare category for creation
        def get_or_prepare_category(system_code=None, code=None, name=None, parent=None, default=True):
            if system_code and system_code in existing_categories_by_system_code:
                return existing_categories_by_system_code[system_code]
            elif code and code in existing_categories:
                return existing_categories[code]
            
            # Create new category object (not saved yet)
            category_data = {
                'name': name,
                'company': self,
                'default': default,
            }
            if system_code:
                category_data['system_code'] = system_code
            if code:
                category_data['code'] = code
            if parent:
                category_data['parent'] = parent
                
            category = Category(**category_data)
            categories_to_create.append(category)
            
            # Add to existing dict so subsequent references work
            if code:
                existing_categories[code] = category
            if system_code:
                existing_categories_by_system_code[system_code] = category
            
            return category

        # Helper function to get or prepare account for creation
        def get_or_prepare_account(system_code=None, code=None, name=None, category=None, default=True):
            if system_code and system_code in existing_accounts_by_system_code:
                return existing_accounts_by_system_code[system_code]
            elif code and code in existing_accounts:
                return existing_accounts[code]
            
            # Create new account object (not saved yet)
            account_data = {
                'name': name,
                'company': self,
                'category': category,
                'default': default,
            }
            if system_code:
                account_data['system_code'] = system_code
            if code:
                account_data['code'] = code
                
            account = Account(**account_data)
            accounts_to_create.append(account)
            
            # Add to existing dict so subsequent references work
            if code:
                existing_accounts[code] = account
            if system_code:
                existing_accounts_by_system_code[system_code] = account
            
            return account

        # CREATE ROOT CATEGORIES
        # ================================================
        root = {}
        for category in Category.ROOT:
            root[category[0]] = get_or_prepare_category(
                system_code=acc_cat_system_codes[category[0]],
                name=category[0],
                code=category[1]
            )

        # Create root categories first since others depend on them (MPTT requires individual saves)
        root_categories = [cat for cat in categories_to_create if cat.parent is None]
        for category in root_categories:
            category.save()
        categories_to_create = [cat for cat in categories_to_create if cat.parent is not None]

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR EQUITY
        # ================================================
        get_or_prepare_account(
            system_code=acc_system_codes["Profit and Loss Account"],
            name="Profit and Loss Account",
            category=root["Equity"],
            code="Q-PL"
        )
        
        get_or_prepare_account(
            code="Q-OBE",
            name="Opening Balance Equity",
            category=root["Equity"]
        )
        
        get_or_prepare_account(
            code="Q-CI",
            name="Capital Investment",
            category=root["Equity"]
        )
        
        get_or_prepare_account(
            code="Q-DC",
            name="Drawing Capital",
            category=root["Equity"]
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR ASSETS
        # ================================================
        get_or_prepare_category(
            code="A-OR",
            name="Other Receivables",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            code="A-DA",
            name="Deferred Assets",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            system_code=acc_cat_system_codes["Fixed Assets"],
            name="Fixed Assets",
            code="A-FA",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            code="A-LA",
            name="Loans and Advances Given",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            code="A-D",
            name="Deposits Made",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            code="A-E",
            name="Employee",
            parent=root["Assets"]
        )
        
        tax_receivables = get_or_prepare_category(
            system_code=acc_cat_system_codes["Tax Receivables"],
            name="Tax Receivables",
            code="A-TR",
            parent=root["Assets"]
        )
        
        get_or_prepare_account(
            system_code=acc_system_codes["TDS Receivables"],
            name="TDS Receivables",
            category=tax_receivables,
            code="A-TR-TDS"
        )

        cash_account_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Cash Accounts"],
            name="Cash Accounts",
            code="A-C",
            parent=root["Assets"]
        )
        
        cash_account = get_or_prepare_account(
            system_code=acc_system_codes["Cash"],
            name="Cash",
            category=cash_account_category,
            code="A-C-C"
        )
        
        get_or_prepare_category(
            code="A-CE",
            name="Cash Equivalent Account",
            parent=root["Assets"]
        )

        get_or_prepare_category(
            system_code=acc_cat_system_codes["Bank Accounts"],
            name="Bank Accounts",
            code="A-B",
            parent=root["Assets"]
        )

        account_receivables = get_or_prepare_category(
            system_code=acc_cat_system_codes["Account Receivables"],
            name="Account Receivables",
            code="A-AR",
            parent=root["Assets"]
        )
        
        get_or_prepare_category(
            system_code=acc_cat_system_codes["Customers"],
            name="Customers",
            code="A-AR-C",
            parent=account_receivables
        )

        get_or_prepare_category(
            code="A-ED",
            name="Employee Deductions",
            parent=root["Assets"]
        )

        # CREATE DEFAULT CATEGORIES AND LEDGERS FOR LIABILITIES
        # =====================================================
        account_payables = get_or_prepare_category(
            system_code=acc_cat_system_codes["Account Payables"],
            name="Account Payables",
            code="L-AP",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            system_code=acc_cat_system_codes["Suppliers"],
            name="Suppliers",
            parent=account_payables,
            code="L-AP-S"
        )
        
        get_or_prepare_category(
            code="L-OP",
            name="Other Payables",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            code="L-P",
            name="Provisions",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            code="L-SL",
            name="Secured Loans",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            code="L-US",
            name="Unsecured Loans",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            code="L-DT",
            name="Deposits Taken",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_category(
            code="L-LA",
            name="Loans & Advances Taken",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_account(
            code="L-DEP",
            name="Provision for Accumulated Depreciation",
            category=root["Liabilities"]
        )
        
        get_or_prepare_account(
            code="L-AFP",
            name="Audit Fee Payable",
            category=root["Liabilities"]
        )
        
        get_or_prepare_account(
            code="L-OP",
            name="Other Payables",
            category=root["Liabilities"]
        )
        
        duties_and_taxes = get_or_prepare_category(
            system_code=acc_cat_system_codes["Duties & Taxes"],
            name="Duties & Taxes",
            code="L-T",
            parent=root["Liabilities"]
        )
        
        get_or_prepare_account(
            code="L-T-I",
            name="Income Tax",
            category=duties_and_taxes
        )
        
        get_or_prepare_account(
            code="L-T-TA",
            name="TDS (Audit Fee)",
            category=duties_and_taxes
        )
        
        get_or_prepare_account(
            code="L-T-TR",
            name="TDS (Rent)",
            category=duties_and_taxes
        )

        # CREATE DEFAULT CATEGORIES FOR INCOME
        # =====================================
        sales_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Sales"],
            name="Sales",
            code="I-S",
            parent=root["Income"]
        )
        
        get_or_prepare_account(
            system_code=acc_system_codes["Sales Account"],
            name="Sales Account",
            code="I-S-S",
            category=sales_category
        )
        
        direct_income = get_or_prepare_category(
            system_code=acc_cat_system_codes["Direct Income"],
            name="Direct Income",
            parent=root["Income"],
            code="I-D"
        )
        
        get_or_prepare_category(
            code="I-D-TR",
            name="Transfer and Remittance",
            parent=direct_income
        )
        
        indirect_income = get_or_prepare_category(
            system_code=acc_cat_system_codes["Indirect Income"],
            name="Indirect Income",
            parent=root["Income"],
            code="I-I"
        )

        discount_income_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Discount Income"],
            name="Discount Income",
            code="I-I-DI",
            parent=indirect_income
        )
        
        get_or_prepare_account(
            system_code=acc_system_codes["Discount Income"],
            name="Discount Income",
            code="I-I-DI-DI",
            category=discount_income_category
        )

        # CREATE DEFAULT CATEGORIES FOR EXPENSES
        # =====================================
        purchase_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Purchase"],
            name="Purchase",
            code="E-P",
            parent=root["Expenses"]
        )
        
        get_or_prepare_account(
            system_code=acc_system_codes["Purchase Account"],
            name="Purchase Account",
            code="E-P-P",
            category=purchase_category
        )

        direct_expenses = get_or_prepare_category(
            system_code=acc_cat_system_codes["Direct Expenses"],
            name="Direct Expenses",
            code="E-D",
            parent=root["Expenses"]
        )

        additional_cost_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Additional Cost"],
            name="Additional Cost",
            code="E-D-AC",
            parent=direct_expenses
        )

        # Handle landed cost accounts
        new_additional_cost_accounts = {}
        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                
                account = get_or_prepare_account(
                    system_code=system_code,
                    name=cost_type,
                    category=additional_cost_category,
                    code=code
                )
                
                # Check if this is a new account we're creating
                if account in accounts_to_create:
                    new_additional_cost_accounts[cost_type] = None  # Will be set after save

        get_or_prepare_category(
            code="E-D-PE",
            name="Purchase Expenses",
            parent=direct_expenses
        )
        
        indirect_expenses = get_or_prepare_category(
            system_code=acc_cat_system_codes["Indirect Expenses"],
            name="Indirect Expenses",
            code="E-I",
            parent=root["Expenses"]
        )

        bank_charges = get_or_prepare_category(
            system_code=acc_cat_system_codes["Bank Charges"],
            name="Bank Charges",
            code="E-I-BC",
            parent=indirect_expenses
        )
        
        get_or_prepare_account(
            code="E-I-BC-BC",
            name="Bank Charges",
            category=bank_charges
        )
        
        get_or_prepare_account(
            code="E-I-FP",
            name="Fines & Penalties",
            category=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-P",
            name="Pay Head",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-FB",
            name="Food and Beverages",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-C",
            name="Communication Expenses",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-CC",
            name="Courier Charges",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-PS",
            name="Printing and Stationery",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-RM",
            name="Repair and Maintenance",
            parent=indirect_expenses
        )
        
        get_or_prepare_category(
            code="E-I-FT",
            name="Fuel and Transport",
            parent=indirect_expenses
        )
        
        discount_expense_category = get_or_prepare_category(
            system_code=acc_cat_system_codes["Discount Expenses"],
            name="Discount Expenses",
            parent=indirect_expenses,
            code="E-I-DE"
        )
        
        get_or_prepare_account(
            system_code=acc_system_codes["Discount Expenses"],
            name="Discount Expenses",
            category=discount_expense_category,
            code="E-I-DE-DE"
        )

        # Opening Balance Difference
        # ==========================
        get_or_prepare_account(
            system_code=acc_system_codes["Opening Balance Difference"],
            name="Opening Balance Difference",
            code="O-OBD",
            category=root["Opening Balance Difference"]
        )

        # For Inventory Adjustment
        # ==========================
        inventory_write_off_account = get_or_prepare_category(
            system_code=acc_cat_system_codes["Inventory Write-off"],
            name="Inventory write-off",
            parent=indirect_expenses,
            code="E-I-DE-IWO"
        )

        get_or_prepare_account(
            system_code=acc_system_codes["Damage Expense"],
            name="Damage Expense",
            code="E-I-DE-IWO-DE",
            category=inventory_write_off_account
        )

        get_or_prepare_account(
            system_code=acc_system_codes["Expiry Expense"],
            name="Expiry Expense",
            code="E-I-DE-IWO-EE",
            category=inventory_write_off_account
        )

        # CREATE CATEGORIES IN ORDER (MPTT REQUIRES INDIVIDUAL SAVES)
        # ===========================================================
        
        # Batch 2: Create second-level categories that are parents to other categories
        parent_category_objects = [
            tax_receivables, cash_account_category, account_receivables, account_payables, 
            duties_and_taxes, sales_category, direct_income, indirect_income, 
            purchase_category, direct_expenses, indirect_expenses
        ]
        second_level_categories = [cat for cat in categories_to_create if cat in parent_category_objects]
        for category in second_level_categories:
            category.save()
        # Remove created categories from the main list
        categories_to_create = [cat for cat in categories_to_create if cat not in second_level_categories]
        
        # Batch 3: Create third-level categories that are parents to other categories  
        third_level_parent_objects = [discount_income_category, additional_cost_category, 
                                     bank_charges, discount_expense_category]
        third_level_categories = [cat for cat in categories_to_create if cat in third_level_parent_objects]
        for category in third_level_categories:
            category.save()
        # Remove created categories from the main list
        categories_to_create = [cat for cat in categories_to_create if cat not in third_level_categories]
        
        # Batch 4: Create remaining categories
        for category in categories_to_create:
            category.save()
            
        # Create all accounts at once since they don't have hierarchical dependencies
        if accounts_to_create:
            Account.objects.bulk_create(accounts_to_create, ignore_conflicts=True)

        # Update landed cost account IDs after bulk create
        if new_additional_cost_accounts:
            # Refresh accounts from DB to get IDs
            created_accounts = Account.objects.filter(
                company=self,
                system_code__startswith="E-D-LC-"
            ).values('system_code', 'id')
            
            account_id_map = {acc['system_code']: acc['id'] for acc in created_accounts}
            
            for cost_type in new_additional_cost_accounts:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{LandedCostRowType.values.index(cost_type)}"
                if system_code in account_id_map:
                    new_additional_cost_accounts[cost_type] = account_id_map[system_code]

        # Handle PurchaseSetting
        purchase_setting, created = PurchaseSetting.objects.get_or_create(company=self)
        if created and new_additional_cost_accounts:
            purchase_setting.landed_cost_accounts = new_additional_cost_accounts
        elif new_additional_cost_accounts:
            purchase_setting.landed_cost_accounts.update(new_additional_cost_accounts)
        if new_additional_cost_accounts:
            purchase_setting.save()

        # Create PaymentMode for Cash if it doesn't exist
        if not PaymentMode.objects.filter(name="Cash", company=self).exists():
            # Get the actual cash account from DB
            actual_cash_account = Account.objects.get(
                company=self,
                system_code=acc_system_codes["Cash"]
            )
            PaymentMode.objects.create(
                name="Cash", 
                company=self, 
                account=actual_cash_account
            )

        # Create default permission for company
        Permission.objects.get_or_create(
            company=self,
            name="Default",
        )

        # Create default settings for company
        SalesSetting.objects.get_or_create(company=self)
        QuotationSetting.objects.get_or_create(
            company=self,
            defaults={
                'body_text': "We are pleased to provide you with the following quotation for the listed items.",
                'footer_text': "<div>Terms and conditions apply.</div><div>We look forward to working with you.</div>",
            }
        )
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