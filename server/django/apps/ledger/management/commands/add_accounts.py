from django.conf import settings
from django.core.management.base import BaseCommand

# from apps.tax.models import TaxScheme
from apps.company.models import Company
from apps.ledger.models import Account, Category


class Command(BaseCommand):
    help = "Change categories and organizations to dynamic relations"

    def handle(self, *args, **options):
        for company in Company.objects.all():
            root = {}
            for category in Category.ROOT:
                root[category[0]] = Category.objects.get(
                    name=category[0], code=category[1], company=company, default=True
                )

            # parent_name = 'Indirect Expenses'
            # parent_code = 'E-I'
            # parent = Category.objects.get(name=parent_name, code=parent_code, company=company, default=True)
            # category_name = 'Bank Charges'
            # category_code = 'E-I-BC'
            # if not Category.objects.filter(name=category_name, company=company).exists():
            #     Category.objects.create(name=category_name, code=category_code, parent=parent, company=company,
            #                             default=True)
            acc_system_codes = settings.ACCOUNT_SYSTEM_CODES

            account_name = "Profit and Loss Account"
            account_code = "Q-PL"
            category = root["Equity"]
            system_code = acc_system_codes[account_name]

            Account.objects.create(
                name=account_name,
                category=category,
                code=account_code,
                company=company,
                default=True,
                system_code=system_code,
            )
