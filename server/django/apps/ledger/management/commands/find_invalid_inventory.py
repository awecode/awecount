from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.product.models import find_obsolete_transactions
from apps.voucher.models import PurchaseVoucher, SalesVoucher


class Command(BaseCommand):
    help = "Find invalid purchase voucher inventory transactions"

    def handle(self, *args, **options):
        pvs = PurchaseVoucher.objects.all()
        for pv in pvs:
            for row in pv.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related("item__account"):
                find_obsolete_transactions(
                    row,
                    pv.date,
                    ["dr", row.item.account, int(row.quantity)],
                )

        svs = SalesVoucher.objects.all()
        print("------------Sales----------------")
        for pv in svs:
            for row in pv.rows.filter(Q(item__track_inventory=True) | Q(item__fixed_asset=True)).select_related("item__account"):
                find_obsolete_transactions(
                    row,
                    pv.date,
                    ["dr", row.item.account, int(row.quantity)],
                )
