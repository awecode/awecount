from django.core.management.base import BaseCommand

from apps.ledger.models import JournalEntry


class Command(BaseCommand):
    help = 'Find journal entries without source transaction'

    def handle(self, *args, **options):
        for jv in JournalEntry.objects.all():
            if not jv.source:
                print(jv.id)
