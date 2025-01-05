from django.core.management.base import BaseCommand

from apps.ledger.models import JournalEntry


class Command(BaseCommand):
    help = "Delete journal entries without source transaction"

    def handle(self, *args, **options):
        cnt = 0
        for jv in JournalEntry.objects.all():
            if not jv.source:
                cnt += 1
                jv.delete()

        print("{} orphan journal entries deleted!".format(cnt))
