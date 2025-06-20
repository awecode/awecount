from django.core.management.base import BaseCommand

# from apps.tax.models import TaxScheme
from apps.company.models import Company
from apps.ledger.models.base import Category, Account
from django.conf import settings

from apps.voucher.models import LandedCostRowType

acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
acc_system_codes = settings.ACCOUNT_SYSTEM_CODES


class Command(BaseCommand):
    help = "Fix system codes for categories and accounts"

    def handle(self, *args, **options):
        categories = {
            "Assets": "A",
            "Account Receivables": "A-AR",
            "Liabilities": "L",
            "Account Payables": "L-AP",
            "Direct Income": "I-D",
            "Indirect Income": "I-I",
            "Equity": "E",
            "Opening Balance Difference": "E-OBD",
            "Inventory write-off": "E-I-DE-IWO",
        }

        for company in Company.objects.all():
            for category_name in categories.keys():
                try:
                    system_code = acc_cat_system_codes.get(category_name)
                    if not system_code:
                        raise Exception(f"System code not found for {category_name}")
                        
                    category = Category.objects.filter(
                        system_code=system_code,
                        company=company,
                    ).first()

                    if category:
                        print(f"Category {category_name} for company {company.name} already has correct system_code: {system_code}")
                        continue
                    
                    category = Category.objects.get(
                        code=categories[category_name],
                        company=company,
                    )

                    if category.system_code == system_code:
                        print(f"Category {category_name} for company {company.name} already has correct system_code: {system_code}")
                        continue
                    
                    category.system_code = system_code
                    category.save()
                    print(
                        f"Updated {category_name} for company {company.name} with system_code: {system_code}"
                    )
                        
                except Category.DoesNotExist:
                    print(
                        f"Category {category_name} not found for company {company.name}"
                    )

        accounts = {
            "Sales Account": "I-S-S",
            "Discount Expenses": "E-I-DE-DE",
        }

        for index, cost_type in enumerate(LandedCostRowType.values):
            if cost_type not in [LandedCostRowType.CUSTOMS_VALUATION_UPLIFT, LandedCostRowType.TAX_ON_PURCHASE]:
                system_code = f"E-D-LC-{cost_type[:3].upper()}{index}"
                accounts[cost_type] = system_code
                acc_system_codes[cost_type] = system_code

        for company in Company.objects.all():
            for account_name in accounts:
                try:
                    # First check if account with system code exists
                    system_code = acc_system_codes.get(account_name)
                    if not system_code:
                        continue
                        
                    # Try to find account by system code first
                    account = Account.objects.filter(
                        system_code=system_code,
                        company=company,
                    ).first()

                    if account:
                        print(f"Account {account_name} for company {company.name} already has correct system_code: {system_code}")
                        continue
                    
                    
                    account = Account.objects.get(
                        code=accounts[account_name],
                        company=company,
                    )

                    if account.system_code == system_code:
                        print(f"Account {account_name} for company {company.name} already has correct system_code: {system_code}")
                        continue
                    
                    account.system_code = system_code
                    account.save()
                    print(
                        f"Updated {account_name} for company {company.name} with system_code: {system_code}"
                    )
                        
                except Account.DoesNotExist:
                    print(
                        f"Account {account_name} not found for company {company.name}"
                    )
