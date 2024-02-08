from django.core.management.base import BaseCommand

from apps.ledger.models import JournalEntry


class Command(BaseCommand):
    help = "Find journal entries without source transaction"

    def handle(self, *args, **options):
        cnt = 0
        for jv in JournalEntry.objects.all():
            if not jv.source:
                cnt += 1
                first = jv.transactions.first()
                print(
                    jv.id,
                    jv.date,
                    jv.content_type,
                    (first.account, first.account.company) if first else "",
                )

        print("{} orphan journal entries!".format(cnt))
