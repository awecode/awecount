from datetime import date

from django.core.management.base import BaseCommand

from apps.voucher.models import RecurringVoucherTemplate
from server.django.apps.voucher.tasks import generate_voucher


class Command(BaseCommand):
    help = "Create vouchers from recurring voucher templates"

    def handle(self, *args, **options):
        today = date.today()
        templates = RecurringVoucherTemplate.objects.filter(
            is_active=True, next_date=today
        )
        for template in templates:
            generate_voucher(template_id=template.id)
