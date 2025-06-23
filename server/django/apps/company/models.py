import json
import re
import uuid
import warnings
from datetime import timedelta
from functools import cached_property
from typing import Dict
from django.db.models import Q

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
    corporate_tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

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

        # Define all categories in a structured way
        CATEGORY_DEFINITIONS = [
            # Root categories
            *[{"name": category[0], "code": category[1], "system_code": acc_cat_system_codes[category[0]]} for category in Category.ROOT],
            
            # Assets subcategories
            {"name": "Other Receivables", "code": "A-OR", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Deferred Assets", "code": "A-DA", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Fixed Assets", "code": "A-FA", "system_code": acc_cat_system_codes["Fixed Assets"], "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Loans and Advances Given", "code": "A-LA", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Deposits Made", "code": "A-D", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Employee", "code": "A-E", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Tax Receivables", "code": "A-TR", "system_code": acc_cat_system_codes["Tax Receivables"], "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Cash Accounts", "code": "A-C", "system_code": acc_cat_system_codes["Cash Accounts"], "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Cash Equivalent Account", "code": "A-CE", "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Bank Accounts", "code": "A-B", "system_code": acc_cat_system_codes["Bank Accounts"], "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Account Receivables", "code": "A-AR", "system_code": acc_cat_system_codes["Account Receivables"], "parent_system_code": acc_cat_system_codes["Assets"]},
            {"name": "Employee Deductions", "code": "A-ED", "parent_system_code": acc_cat_system_codes["Assets"]},
            
            # Account Receivables subcategories
            {"name": "Customers", "code": "A-AR-C", "system_code": acc_cat_system_codes["Customers"], "parent_system_code": acc_cat_system_codes["Account Receivables"]},
            
            # Liabilities subcategories
            {"name": "Account Payables", "code": "L-AP", "system_code": acc_cat_system_codes["Account Payables"], "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Other Payables", "code": "L-OP", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Provisions", "code": "L-P", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Secured Loans", "code": "L-SL", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Unsecured Loans", "code": "L-US", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Deposits Taken", "code": "L-DT", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Loans & Advances Taken", "code": "L-LA", "parent_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Duties & Taxes", "code": "L-T", "system_code": acc_cat_system_codes["Duties & Taxes"], "parent_system_code": acc_cat_system_codes["Liabilities"]},
            
            # Account Payables subcategories
            {"name": "Suppliers", "code": "L-AP-S", "system_code": acc_cat_system_codes["Suppliers"], "parent_system_code": acc_cat_system_codes["Account Payables"]},
            
            # Income subcategories
            {"name": "Sales", "code": "I-S", "system_code": acc_cat_system_codes["Sales"], "parent_system_code": acc_cat_system_codes["Income"]},
            {"name": "Direct Income", "code": "I-D", "system_code": acc_cat_system_codes["Direct Income"], "parent_system_code": acc_cat_system_codes["Income"]},
            {"name": "Indirect Income", "code": "I-I", "system_code": acc_cat_system_codes["Indirect Income"], "parent_system_code": acc_cat_system_codes["Income"]},
            
            # Direct Income subcategories
            {"name": "Transfer and Remittance", "code": "I-D-TR", "parent_system_code": acc_cat_system_codes["Direct Income"]},
            
            # Indirect Income subcategories
            {"name": "Discount Income", "code": "I-I-DI", "system_code": acc_cat_system_codes["Discount Income"], "parent_system_code": acc_cat_system_codes["Indirect Income"]},
            {"name": "Interest Income", "code": "I-I-II", "system_code": acc_cat_system_codes["Interest Income"], "parent_system_code": acc_cat_system_codes["Indirect Income"]},
            
            # Expenses subcategories
            {"name": "Purchase", "code": "E-P", "system_code": acc_cat_system_codes["Purchase"], "parent_system_code": acc_cat_system_codes["Expenses"]},
            {"name": "Direct Expenses", "code": "E-D", "system_code": acc_cat_system_codes["Direct Expenses"], "parent_system_code": acc_cat_system_codes["Expenses"]},
            {"name": "Indirect Expenses", "code": "E-I", "system_code": acc_cat_system_codes["Indirect Expenses"], "parent_system_code": acc_cat_system_codes["Expenses"]},
            
            # Direct Expenses subcategories
            {"name": "Additional Cost", "code": "E-D-AC", "system_code": acc_cat_system_codes["Additional Cost"], "parent_system_code": acc_cat_system_codes["Direct Expenses"]},
            {"name": "Purchase Expenses", "code": "E-D-PE", "parent_system_code": acc_cat_system_codes["Direct Expenses"]},
            
            # Indirect Expenses subcategories
            {"name": "Bank Charges", "code": "E-I-BC", "system_code": acc_cat_system_codes["Bank Charges"], "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Pay Head", "code": "E-I-P", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Food and Beverages", "code": "E-I-FB", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Communication Expenses", "code": "E-I-C", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Courier Charges", "code": "E-I-CC", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Printing and Stationery", "code": "E-I-PS", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Repair and Maintenance", "code": "E-I-RM", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Fuel and Transport", "code": "E-I-FT", "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Discount Expenses", "code": "E-I-DE", "system_code": acc_cat_system_codes["Discount Expenses"], "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Interest Expenses", "code": "E-I-IE", "system_code": acc_cat_system_codes["Interest Expenses"], "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Inventory write-off", "code": "E-I-DE-IWO", "system_code": acc_cat_system_codes["Inventory write-off"], "parent_system_code": acc_cat_system_codes["Indirect Expenses"]},
        ]

        # Define all accounts in a structured way
        ACCOUNT_DEFINITIONS = [
            # Equity accounts
            {"name": "Profit and Loss Account", "code": "Q-PL", "system_code": acc_system_codes["Profit and Loss Account"], "category_system_code": acc_cat_system_codes["Equity"]},
            {"name": "Opening Balance Equity", "code": "Q-OBE", "category_system_code": acc_cat_system_codes["Equity"]},
            {"name": "Capital Investment", "code": "Q-CI", "category_system_code": acc_cat_system_codes["Equity"]},
            {"name": "Drawing Capital", "code": "Q-DC", "category_system_code": acc_cat_system_codes["Equity"]},
            
            # Asset accounts
            {"name": "TDS Receivables", "code": "A-TR-TDS", "system_code": acc_system_codes["TDS Receivables"], "category_system_code": acc_cat_system_codes["Tax Receivables"]},
            {"name": "Cash", "code": "A-C-C", "system_code": acc_system_codes["Cash"], "category_system_code": acc_cat_system_codes["Cash Accounts"]},
            
            # Liability accounts
            {"name": "Provision for Accumulated Depreciation", "code": "L-DEP", "category_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Audit Fee Payable", "code": "L-AFP", "category_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Other Payables", "code": "L-OP", "category_system_code": acc_cat_system_codes["Liabilities"]},
            {"name": "Income Tax", "code": "L-T-I", "category_system_code": acc_cat_system_codes["Duties & Taxes"]},
            {"name": "TDS (Audit Fee)", "code": "L-T-TA", "category_system_code": acc_cat_system_codes["Duties & Taxes"]},
            {"name": "TDS (Rent)", "code": "L-T-TR", "category_system_code": acc_cat_system_codes["Duties & Taxes"]},
            
            # Income accounts
            {"name": "Sales Account", "code": "I-S-S", "system_code": acc_system_codes["Sales Account"], "category_system_code": acc_cat_system_codes["Sales"]},
            {"name": "Discount Income", "code": "I-I-DI-DI", "system_code": acc_system_codes["Discount Income"], "category_system_code": acc_cat_system_codes["Discount Income"]},
            {"name": "Interest Income", "code": "I-I-II-II", "system_code": acc_system_codes["Interest Income"], "category_system_code": acc_cat_system_codes["Interest Income"]},
            
            # Expense accounts
            {"name": "Purchase Account", "code": "E-P-P", "system_code": acc_system_codes["Purchase Account"], "category_system_code": acc_cat_system_codes["Purchase"]},
            {"name": "Bank Charges", "code": "E-I-BC-BC", "category_system_code": acc_cat_system_codes["Bank Charges"]},
            {"name": "Fines & Penalties", "code": "E-I-FP", "category_system_code": acc_cat_system_codes["Indirect Expenses"]},
            {"name": "Discount Expenses", "code": "E-I-DE-DE", "system_code": acc_system_codes["Discount Expenses"], "category_system_code": acc_cat_system_codes["Discount Expenses"]},
            {"name": "Interest Expenses", "code": "E-I-IE-IE", "system_code": acc_system_codes["Interest Expenses"], "category_system_code": acc_cat_system_codes["Interest Expenses"]},
            
            # Special accounts
            {"name": "Opening Balance Difference", "code": "O-OBD", "system_code": acc_system_codes["Opening Balance Difference"], "category_system_code": acc_cat_system_codes["Opening Balance Difference"]},
            {"name": "Damage Expense", "code": "E-I-DE-IWO-DE", "system_code": acc_system_codes["Damage Expense"], "category_system_code": acc_cat_system_codes["Inventory write-off"]},
            {"name": "Expiry Expense", "code": "E-I-DE-IWO-EE", "system_code": acc_system_codes["Expiry Expense"], "category_system_code": acc_cat_system_codes["Inventory write-off"]},
        ]

        CATEGORY_CODES = [cat["code"] for cat in CATEGORY_DEFINITIONS if "system_code" not in cat]
        ACCOUNT_CODES = [acc["code"] for acc in ACCOUNT_DEFINITIONS if "system_code" not in acc]
        
        landed_cost_system_codes = []
        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                landed_cost_system_codes.append(system_code)
        
        all_account_system_codes = list(acc_system_codes.values()) + landed_cost_system_codes
        
        category_filter = Q(code__in=CATEGORY_CODES) | Q(system_code__in=acc_cat_system_codes.values())
        filtered_categories = Category.objects.filter(company=self).filter(category_filter)
        
        existing_categories_by_code = {}
        existing_categories_by_system_code = {}
        
        for cat in filtered_categories:
            if cat.system_code:
                existing_categories_by_system_code[cat.system_code] = cat
            else:
                existing_categories_by_code[cat.code] = cat

        account_filter = Q(code__in=ACCOUNT_CODES) | Q(system_code__in=all_account_system_codes)
        filtered_accounts = Account.objects.filter(company=self).filter(account_filter)
        
        existing_accounts_by_code = {}
        existing_accounts_by_system_code = {}
        
        for acc in filtered_accounts:
            if acc.system_code:
                existing_accounts_by_system_code[acc.system_code] = acc
            else:
                existing_accounts_by_code[acc.code] = acc

        accounts_to_create = []

        def get_or_create_category(name, code=None, system_code=None, parent=None):
            if not name:
                raise ValueError("name is required")

            if not code:
                raise ValueError("code is required")
            
            if system_code:
                if system_code in existing_categories_by_system_code:
                    return existing_categories_by_system_code[system_code]
            elif code in existing_categories_by_code:
                return existing_categories_by_code[code]
            
            category = Category.objects.create(
                name=name,
                company=self,
                parent=parent,
                code=code,
                default=True,
                system_code=system_code,
            )

            if system_code:
                existing_categories_by_system_code[system_code] = category
            elif code:
                existing_categories_by_code[code] = category
            
            return category


        def get_or_prepare_account(code, name, system_code=None, category=None):
            if not code:
                raise ValueError("code is required")
            if not name:
                raise ValueError("name is required")
            
            if system_code:
                if system_code in existing_accounts_by_system_code:
                    return existing_accounts_by_system_code[system_code], False
            elif code in existing_accounts_by_code:
                return existing_accounts_by_code[code], False

            account_data = {
                'name': name,
                'company': self,
                'category': category,
                'default': True,
                'code': code,
                'system_code': system_code,
            }
            
                
            account = Account(**account_data)
            accounts_to_create.append(account)

            if system_code:
                existing_accounts_by_system_code[system_code] = account
            else:
                existing_accounts_by_code[code] = account
            
            return account, True

        

        for category_def in CATEGORY_DEFINITIONS:
            parent_system_code = category_def.get("parent_system_code")
            parent = existing_categories_by_system_code[parent_system_code] if parent_system_code else None
            
            get_or_create_category(
                name=category_def["name"],
                code=category_def["code"],
                system_code=category_def.get("system_code"),
                parent=parent
            )
            
        

        for account_def in ACCOUNT_DEFINITIONS:
            category_system_code = account_def.get("category_system_code")
            category = existing_categories_by_system_code.get(category_system_code) if category_system_code else None
            
            get_or_prepare_account(
                name=account_def["name"],
                code=account_def["code"],
                system_code=account_def.get("system_code"),
                category=category
            )
            
        # Get specific categories needed for landed cost accounts
        additional_cost_category = existing_categories_by_system_code[acc_cat_system_codes["Additional Cost"]]

        new_additional_cost_accounts = {}
        new_additional_cost_accounts_system_codes = []
        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                
                _, is_new = get_or_prepare_account(
                    system_code=system_code,
                    name=cost_type,
                    category=additional_cost_category,
                    code=code
                )
                
                if is_new:
                    new_additional_cost_accounts[cost_type] = None
                    new_additional_cost_accounts_system_codes.append(system_code)

        # Handle landed cost accounts (kept separate due to special logic)
        if accounts_to_create:
            Account.objects.bulk_create(accounts_to_create)

        if new_additional_cost_accounts:
            created_accounts = Account.objects.filter(
                company=self,
                system_code__in=new_additional_cost_accounts_system_codes
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

        PaymentMode.objects.get_or_create(
            company=self,
            name="Cash",
            defaults={
                'account': existing_accounts_by_system_code[acc_system_codes["Cash"]]
            }
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