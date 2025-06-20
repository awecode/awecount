from django.core.management.base import BaseCommand

# from apps.tax.models import TaxScheme
from apps.company.models import Company
from apps.ledger.models import Category
from django.conf import settings

acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES


class Command(BaseCommand):
    help = "Change categories and organizations to dynamic relations"

    def handle(self, *args, **options):
        categories = [
            "Assets",
            "Account Receivables",
            "Liabilities",
            "Account Payables",
            "Direct Income",
            "Indirect Income",
            "Equity",
            "Opening Balance Difference",
        ]

        for company in Company.objects.all():
            for category_name in categories:
                try:
                    # First check if category with system code exists
                    system_code_mapping = {
                        "Assets": acc_cat_system_codes["Assets"],
                        "Account Receivables": acc_cat_system_codes["Account Receivables"], 
                        "Liabilities": acc_cat_system_codes["Liabilities"],
                        "Account Payables": acc_cat_system_codes["Account Payables"],
                        "Direct Income": acc_cat_system_codes["Direct Income"],
                        "Indirect Income": acc_cat_system_codes["Indirect Income"],
                        "Equity": acc_cat_system_codes["Equity"],
                        "Opening Balance Difference": acc_cat_system_codes["Opening Balance Difference"],
                    }
                    
                    system_code = system_code_mapping.get(category_name)
                    if not system_code:
                        continue
                        
                    # Try to find category by system code first
                    category = Category.objects.filter(
                        system_code=system_code,
                        company=company,
                        parent__isnull=True
                    ).first()
                    
                    # If not found by system code, try by name
                    if not category:
                        category = Category.objects.get(
                            name=category_name,
                            company=company,
                            parent__isnull=True
                        )
                    
                    # Update system code if it's different
                    if category.system_code != system_code:
                        category.system_code = system_code
                        category.save()
                        print(
                            f"Updated {category_name} for company {company.name} with system_code: {system_code}"
                        )
                    else:
                        print(
                            f"Category {category_name} for company {company.name} already has correct system_code: {system_code}"
                        )
                        
                except Category.DoesNotExist:
                    print(
                        f"Category {category_name} not found for company {company.name}"
                    )
