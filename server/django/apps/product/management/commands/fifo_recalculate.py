from django.core.management.base import BaseCommand
from django.db.models import F, Func, Sum, Window

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

        # * Step 1: Find the first transaction which has FIFO inconsistency
        first_txn_to_fix = (
            base_qs.filter(fifo_inconsistency_quantity__gt=0)
            .exclude(journal_entry__content_type__model="debitnoterow")
            .order_by("journal_entry__date", "id")
            .first()
        )

        if not first_txn_to_fix:
            print("No FIFO inconsistency to fix")
            return

        # * Step 2: Find the transactions after the first transaction which has FIFO inconsistency
        # * This is because, the first transaction which has FIFO inconsistency has probably
        # * caused the FIFO inconsistency in the transactions after it.
        # * While doing so, we also exclude the transactions of debit notes, because they are not to be touched
        txns_to_probably_fix = (
            base_qs.filter(
                journal_entry__date__gte=first_txn_to_fix.journal_entry.date,
                id__gte=first_txn_to_fix.id,
            )
            .exclude(journal_entry__content_type__model="debitnoterow")
            .order_by("journal_entry__date", "id")
        )

        # * Step 3: Find the transactions which have been consumed by the transactions which have or may have FIFO inconsistency
        # * This is because, we need to replenish the consumed transactions, so that it could be re-evaluated for FIFO consumption
        txn_ids_to_replenish = (
            txns_to_probably_fix.annotate(
                dr_txn_id=Func(F("consumption_data"), function="jsonb_object_keys")
            )
            .values_list("dr_txn_id", flat=True)
            .order_by("dr_txn_id")
            .distinct()
        )

        txns_to_replenish = base_qs.filter(id__in=list(txn_ids_to_replenish))

        replenished_txns = [
            txn
            for txn in txns_to_replenish
            if not setattr(txn, "remaining_quantity", getattr(txn, "dr_amount"))
        ]

        # * We can do this and this won't affect the transactions of debit notes
        # * Because, the transactions of debit notes are not included in the `txns_to_replenish`
        # * which is because, credit transaction won't have the debit transaction id against
        # * which debit note is issued, as it's removed while creating the debit note
        Transaction.objects.bulk_update(replenished_txns, ["remaining_quantity"])

        # * Step 4: Now transaction which have or may have FIFO inconsistency, we need to forcedully declare them inconsistent
        txns_to_declare_inconsistent = []

        for txn in txns_to_probably_fix:
            txn.fifo_inconsistency_quantity = txn.cr_amount
            txn.consumption_data = {}
            txns_to_declare_inconsistent.append(txn)

        Transaction.objects.bulk_update(
            txns_to_declare_inconsistent,
            ["fifo_inconsistency_quantity", "consumption_data"],
        )

        # * Step 5: Now we need to find the transactions which can be consumed and to fix the transactions which have FIFO inconsistency
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

        # * Step 6: Now we need to fulfill the transactions which have FIFO inconsistency
        # * by consuming the transactions which can be consumed

        total_quantity_to_fulfill = txns_to_fix[len(txns_to_fix) - 1].running

        txns_can_be_consumed_lte = txns_can_be_consumed.filter(
            running__lte=total_quantity_to_fulfill
        )

        if len(txns_can_be_consumed_lte):
            # * if the cumulative remaining quantity of the transactions is less than the required quantity fetch the next transaction as well
            # * the last transaction i.e. the one with the highest running (< req_qty)
            txn_highest = txns_can_be_consumed_lte[len(txns_can_be_consumed_lte) - 1]
            if txn_highest.running < total_quantity_to_fulfill:
                tx_next = txns_can_be_consumed.filter(
                    running__gt=total_quantity_to_fulfill
                ).first()
                if tx_next:
                    txns_can_be_consumed_lte = txns_can_be_consumed_lte.union(tx_next)
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
