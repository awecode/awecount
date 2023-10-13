from rest_framework.response import Response

from django.db.models import F

from apps.voucher.models import (
    Challan,
    ChallanRow,
    PurchaseVoucherRow,
    SalesVoucher,
    SalesVoucherRow,
)
from awecount.libs.exception import UnprocessableException


def fifo_update_purchase_rows(rows):
    for row in rows:
        sold_items = row.sold_items
        updates = [
            PurchaseVoucherRow.objects.filter(id=key).update(
                remaining_quantity=F("remaining_quantity") + value
            )
            for key, value in sold_items.items()
        ]
        row.sold_items = {}
        row.save()


def fifo_cancel_sales(voucher, allow_fifo_inconsistency: bool = False):
    rows = voucher.rows.all()
    if allow_fifo_inconsistency:
        fifo_update_purchase_rows(rows)
        return Response({})
    else:
        sold_item_dicts = rows.values_list("sold_items", flat=True)
        keys = []
        for dct in sold_item_dicts:
            for k, v in dct.items():
                if int(k) not in keys:
                    keys.append(int(k))
        row_class_map = {SalesVoucher: SalesVoucherRow, Challan: ChallanRow}
        existing_sales = row_class_map[voucher.__class__].objects.filter(
            sold_items__has_keys=keys,
            voucher__issue_datetime__gt=voucher.issue_datetime,
        )

        if existing_sales.exists():
            raise UnprocessableException(
                detail="This action may create inconsistencies in FIFO.",
                code="fifo_inconsistency",
            )
        else:
            fifo_update_purchase_rows(rows)
            return Response({})
        

def fifo_handle_sales_create(request, row):
    if request.company.inventory_setting.enable_fifo:
        item_id = row.get("item_id")
        quantity = row.get("quantity")
        purchase_rows = PurchaseVoucherRow.objects.filter(
            item_id=item_id,
            remaining_quantity__gt=0
        ).order_by("voucher__date", "id")
        sold_items = {}
        for purchase_row in purchase_rows:
            if purchase_row.remaining_quantity == quantity:
                purchase_row.remaining_quantity = 0
                purchase_row.save()
                sold_items[purchase_row.id] = quantity
                break
            elif purchase_row.remaining_quantity > quantity:
                purchase_row.remaining_quantity -= quantity
                purchase_row.save()
                sold_items[purchase_row.id] = quantity
                break
            else:
                quantity -= purchase_row.remaining_quantity
                sold_items[purchase_row.id] = purchase_row.remaining_quantity
                purchase_row.remaining_quantity = 0
                purchase_row.save()
        return sold_items
