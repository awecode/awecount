from rest_framework.response import Response

from django.db.models import F
from apps.product.models import Item

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
        

def fifo_handle_sales_create(row):
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


def handle_quantity_decrease(db_row, row, diff):
    # import ipdb; ipdb.set_trace()
    diff = abs(diff)
    r_diff = db_row.remaining_quantity - diff
    row["remaining_quantity"] = r_diff if r_diff>0 else 0
    db_row.remaining_quantity = r_diff
    db_row.save()
    
    # db_row.remaining_quantity += diff
    # db_row.save()
    sales_rows = SalesVoucherRow.objects.filter(sold_items__has_key=str(row.get("id"))).order_by("-id")
    sales_rows_ids = sales_rows.values_list("id", flat=True)
    # import ipdb; ipdb.set_trace()
    sales_voucher_ids = sales_rows.values_list("voucher", flat=True)
    sales_vouchers = SalesVoucher.objects.filter(id__in=sales_voucher_ids)
    for voucher in sales_vouchers:
        res = fifo_cancel_sales(voucher, False)
    sales_rows = SalesVoucherRow.objects.filter(id__in=sales_rows_ids).order_by("-id")

    for sales_row in sales_rows:
        row = {
            "item_id": sales_row.item_id,
            "quantity": sales_row.quantity
        }
        sold_items = fifo_handle_sales_create(sales_row)
        sales_row.sold_items = sold_items
        sales_row.save()

        # sold_items = sales_row.sold_items
        # sold_quantity = sold_items[str(row["id"])]
        # if sold_quantity > diff:
        #     sold_quantity -= diff
        #     sold_items[str(row["id"])] = sold_quantity
        #     purchase_rows = PurchaseVoucherRow.objects.filter(
        #         item_id=sales_row.item_id,
        #         remaining_quantity__gt=0
        #         ).order_by("voucher__date", "id")
        #     for purchase_row in purchase_rows:
        #         if purchase_row.remaining_quantity == diff:
        #             purchase_row.remaining_quantity = 0
        #             purchase_row.save()
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += diff
        #             else:
        #                 sold_items[str(purchase_row.id)] = diff
        #             break
        #         elif purchase_row.remaining_quantity > diff:
        #             purchase_row.remaining_quantity -= diff
        #             purchase_row.save()
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += diff
        #             else:
        #                 sold_items[str(purchase_row.id)] = diff
        #             break
        #         else:
        #             diff -= purchase_row.remaining_quantity
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += purchase_row.remaining_quantity
        #             else:
        #                 sold_items[str(purchase_row.id)] = purchase_row.remaining_quantity
        #             purchase_row.remaining_quantity = 0
        #             purchase_row.save()
        #     sales_row.sold_items = sold_items
        #     sales_row.save()
        #     break
        # else:
        #     sold_quantity = sold_items.pop(str(row["id"]))
        #     qt = diff - sold_quantity
        #     sold_items[str(row["id"])] = qt
        #     purchase_rows = PurchaseVoucherRow.objects.filter(
        #         item_id=sales_row.item_id,
        #         remaining_quantity__gt=0
        #         ).order_by("voucher__date", "id")
        #     for purchase_row in purchase_rows:
        #         if purchase_row.remaining_quantity == diff:
        #             purchase_row.remaining_quantity = 0
        #             purchase_row.save()
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += diff
        #             else:
        #                 sold_items[str(purchase_row.id)] = diff
        #             break
        #         elif purchase_row.remaining_quantity > diff:
        #             purchase_row.remaining_quantity -= diff
        #             purchase_row.save()
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += diff
        #             else:
        #                 sold_items[str(purchase_row.id)] = diff
        #             break
        #         else:
        #             diff -= purchase_row.remaining_quantity
        #             if str(purchase_row.id) in sold_items.keys():
        #                 sold_items[str(purchase_row.id)] += purchase_row.remaining_quantity
        #             else:
        #                 sold_items[str(purchase_row.id)] = purchase_row.remaining_quantity
        #             purchase_row.remaining_quantity = 0
        #             purchase_row.save()
        #     sales_row.sold_items = sold_items
        #     sales_row.save()

def fifo_handle_purchase_update(voucher, row):
    import ipdb; ipdb.set_trace()
    pass
    # item = Item.objects.get(id=row["item_id"])
    # if item.track_inventory:
    #     if row.get("id"):
    #         db_row = voucher.rows.get(id=row["id"])
    #         diff = row["quantity"] - db_row.quantity
    #         if diff>=0:
    #             row["remaining_quantity"] = db_row.remaining_quantity + diff
    #         else:
    #             # handle_quantity_decrease(db_row, row, diff) 
    #             import ipdb; ipdb.set_trace()
    #             pass
    #     else:
    #         row["remaining_quantity"] = row["quantity"]
    # return row
