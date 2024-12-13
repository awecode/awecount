from datetime import date

from django.core.management.base import BaseCommand

from apps.voucher.models import RecurringVoucherTemplate


class Command(BaseCommand):
    help = "Create vouchers from recurring voucher templates"

    def handle(self, *args, **options):
        today = date.today()
        templates = RecurringVoucherTemplate.objects.filter(
            is_active=True, next_date=today
        )
        for template in templates:
            template.generate_voucher()
