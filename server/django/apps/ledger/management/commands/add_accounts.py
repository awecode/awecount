from django.core.management.base import BaseCommand

from apps.ledger.models import Category, Account
from apps.tax.models import TaxScheme
from apps.users.models import Company


class Command(BaseCommand):
    help = 'Change categories and organizations to dynamic relations'

    def handle(self, *args, **options):
        for company in Company.objects.all():
            duties_and_taxes = Category.objects.get(name='Duties & Taxes', code='L-T', company=company, default=True)
            Account.objects.create(name='Income Tax', category=duties_and_taxes, code='L-T-I', company=company, default=True)
            Account.objects.create(name='TDS (Audit Fee)', category=duties_and_taxes, code='L-T-TA', company=company,
                                   default=True)
            Account.objects.create(name='TDS (Rent)', category=duties_and_taxes, code='L-T-TR', company=company,
                                   default=True)

            TaxScheme.objects.create(name='TDS (Social Security Tax)', short_name='TDS-SST', rate='1', recoverable=False,
                                     default=True,
                                     company=company)

            liabilities = Category.objects.get(name='Liabilities', code='L', company=company, default=True)
            Account.objects.create(name='Provision for Accumulated Depreciation', category=liabilities, code='L-DEP',
                                   company=company, default=True)
            Account.objects.create(name='Audit Fee Payable', category=liabilities, code='L-AFP', company=company, default=True)
            Account.objects.create(name='Other Payables', category=liabilities, code='L-OP', company=company, default=True)

            indirect_expenses = Category.objects.get(name='Indirect Expenses', code='E-I', company=company, default=True)
            Account.objects.create(name='Bank Charges', category=indirect_expenses, code='E-I-BC', company=company, default=True)
            Account.objects.create(name='Fines & Penalties', category=indirect_expenses, code='E-I-FP', company=company,
                                   default=True)

            equity = Category.objects.get(name='Equity', code='Q', company=company, default=True)
            Account.objects.create(name='Capital Investment', category=equity, code='Q-CI', company=company, default=True)
            Account.objects.create(name='Drawing Capital', category=equity, code='Q-DC', company=company, default=True)
