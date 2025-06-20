from django.core.management.base import BaseCommand

# from apps.tax.models import TaxScheme
from apps.company.models import Company


class Command(BaseCommand):
    help = "Create defaults for a company if not exists"

    def handle(self, *args, **options):
        for company in Company.objects.all():
            print("Creating defaults for company: ", company.name)
            company.create_company_defaults()
            print("Done")