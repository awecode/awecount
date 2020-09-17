from django.core.management.base import BaseCommand

from apps.ledger.models import Category, Account
# from apps.tax.models import TaxScheme
from apps.users.models import Company


class Command(BaseCommand):
    help = 'Change categories and organizations to dynamic relations'

    def handle(self, *args, **options):
        for company in Company.objects.all():
            indirect_expenses = Category.objects.get(name='Indirect Expenses', code='E-I', company=company, default=True)

            # Category.objects.create(name='Food and Beverages', code='E-I-FB', parent=indirect_expenses, company=company,
            #                         default=True)
            # Category.objects.create(name='Communication Expenses', code='E-I-C', parent=indirect_expenses, company=company,
            #                         default=True)
            # Category.objects.create(name='Courier Charges', code='E-I-CC', parent=indirect_expenses, company=company,
            #                         default=True)
            # Category.objects.create(name='Printing and Stationery', code='E-I-PS', parent=indirect_expenses, company=company,
            #                         default=True)
            # Category.objects.create(name='Repair and Maintenance', code='E-I-RM', parent=indirect_expenses, company=company,
            #                         default=True)
            # Category.objects.create(name='Fuel and Transport', code='E-I-FT', parent=indirect_expenses, company=company,
            #                         default=True)

            if not Category.objects.filter(name='Bank Charges').exists():
                Category.objects.create(name='Bank Charges', code='E-I-BC', parent=indirect_expenses, company=company,
                                        default=True)
