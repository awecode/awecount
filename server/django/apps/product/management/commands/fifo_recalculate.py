from django.core.management.base import BaseCommand
from django.db.models import Sum, Window

from apps.product.models import Transaction


class Command(BaseCommand):
    help = "Recalculate FIFO"

    def add_arguments(self, parser):
        parser.add_argument(
            "--company",
            type=int,
            help="Company ID",
            required=True,
        )

        parser.add_argument(
            "--item",
            type=int,
            help="Item ID",
            required=True,
        )

    def handle(self, *args, **options):
        base_qs = Transaction.objects.filter(
            account__company__id=options["company"], account__item__id=options["item"]
        )

        txns_can_be_consumed = (
            base_qs.filter(cr_amount=None, remaining_quantity__gt=0)
            .annotate(
                running=Window(
                    expression=Sum("remaining_quantity"),
                    order_by=["journal_entry__date", "id"],
                )
            )
            .order_by("journal_entry__date", "id")
            .only("id", "remaining_quantity")
        )

        if len(txns_can_be_consumed) == 0:
            print("No transactions to consume")
            return

        txns_to_fix = (
            base_qs.filter(fifo_inconsistency_quantity__gt=0)
            .annotate(
                running=Window(
                    expression=Sum("fifo_inconsistency_quantity"),
                    order_by=["journal_entry__date", "id"],
                )
            )
            .order_by("journal_entry__date", "id")
            .exclude(journal_entry__content_type__model="debitnoterow")
        )

        if len(txns_to_fix) == 0:
            print("No transactions to fix")
            return

        total_quantity_to_fulfill = txns_to_fix[len(txns_to_fix) - 1].running

        txns_can_be_consumed_lte = txns_can_be_consumed.filter(
            running__lte=total_quantity_to_fulfill
        )

        if len(txns_can_be_consumed_lte):
            # if the cumulative remaining quantity of the transactions is less than the required quantity fetch the next transaction as well
            # the last transaction i.e. the one with the highest running (< req_qty)
            txn_highest = txns_can_be_consumed_lte[len(txns_can_be_consumed_lte) - 1]
            if txn_highest.running < total_quantity_to_fulfill:
                tx_next = txns_can_be_consumed.filter(
                    running__gt=total_quantity_to_fulfill
                ).first()
                if tx_next:
                    txns_can_be_consumed_lte.union(tx_next)
        else:
            txns_can_be_consumed_lte = txns_can_be_consumed.filter(
                running__gt=total_quantity_to_fulfill
            )[:1]

        for txn_to_fix in txns_to_fix:
            for consumable in txns_can_be_consumed_lte:
                if (
                    consumable.remaining_quantity == 0
                    or txn_to_fix.fifo_inconsistency_quantity == 0
                ):
                    continue
                    # txn_to_fix.fifo_inconsistency_quantity = max(0, txn_to_fix.fifo_inconsistency_quantity - txn.remaining_quantity)
                    # txn_to_fix.consumption_data[txn.id] = [
                    #         txn.fifo_inconsistency_quantity,
                    #         txn.rate,
                    # ]
                    # txn.remaining_quantity -= txn.fifo_inconsistency_quantity
                if (
                    txn_to_fix.fifo_inconsistency_quantity
                    < consumable.remaining_quantity
                ):
                    txn_to_fix.consumption_data[consumable.id] = [
                        txn_to_fix.fifo_inconsistency_quantity,
                        consumable.rate,
                    ]
                    consumable.remaining_quantity -= (
                        txn_to_fix.fifo_inconsistency_quantity
                    )
                    txn_to_fix.fifo_inconsistency_quantity = 0
                elif (
                    txn_to_fix.fifo_inconsistency_quantity
                    >= consumable.remaining_quantity
                ):
                    txn_to_fix.fifo_inconsistency_quantity -= (
                        consumable.remaining_quantity
                    )
                    txn_to_fix.consumption_data[consumable.id] = [
                        consumable.remaining_quantity,
                        consumable.rate,
                    ]
                    consumable.remaining_quantity = 0

        Transaction.objects.bulk_update(
            txns_to_fix,
            [
                "remaining_quantity",
                "consumption_data",
                "fifo_inconsistency_quantity",
            ],
        )
        Transaction.objects.bulk_update(
            txns_can_be_consumed_lte,
            [
                "remaining_quantity",
                "consumption_data",
                "fifo_inconsistency_quantity",
            ],
        )
