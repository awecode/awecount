from django.db.models import F
from rest_framework.response import Response

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
        if sold_items:
            sold_items.pop("OB", None)
        if sold_items:
            updates = [PurchaseVoucherRow.objects.filter(id=key).update(remaining_quantity=F("remaining_quantity") + value[0]) for key, value in sold_items.items()]
        row.sold_items = {}
        row.save()


def update_opening_balance(sold_item):
    dct = sold_item.get("sold_items")
    if dct and dct.get("OB"):
        ob = dct.pop("OB")
        item = Item.objects.get(id=sold_item.get("item_id"))
        item.account.opening_quantity = ob[0]
        item.account.save()


def fifo_cancel_sales(voucher, allow_fifo_inconsistency: bool = False):
    rows = voucher.rows.all()
    sold_items = rows.values("item_id", "sold_items")
    if allow_fifo_inconsistency:
        if sold_items:
            for sold_item in sold_items:
                update_opening_balance(sold_item)
        fifo_update_purchase_rows(rows)
        return Response({})
    else:
        keys = []
        if sold_items:
            for sold_item in sold_items:
                update_opening_balance(sold_item)
                sold_item_dict = sold_item["sold_items"]
                if sold_item_dict:
                    for k, v in sold_item_dict.items():
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
    sold_items = {}

    inv_account = Item.objects.get(id=row["item_id"]).account
    if inv_account and inv_account.opening_quantity:
        if quantity > inv_account.opening_quantity:
            sold_items["OB"] = [inv_account.opening_quantity, inv_account.opening_balance_rate]
            quantity -= inv_account.opening_quantity
            inv_account.opening_quantity = 0
            inv_account.save()
        else:
            inv_account.opening_quantity -= quantity
            inv_account.save()
            sold_items["OB"] = [quantity, inv_account.opening_balance_rate]
            return sold_items

    purchase_rows = PurchaseVoucherRow.objects.filter(item_id=item_id, remaining_quantity__gt=0).order_by("voucher__date", "id")

    for purchase_row in purchase_rows:
        if purchase_row.remaining_quantity == quantity:
            purchase_row.remaining_quantity = 0
            purchase_row.save()
            sold_items[purchase_row.id] = [quantity, purchase_row.rate]
            break
        elif purchase_row.remaining_quantity > quantity:
            purchase_row.remaining_quantity -= quantity
            purchase_row.save()
            sold_items[purchase_row.id] = [quantity, purchase_row.rate]
            break
        else:
            quantity -= purchase_row.remaining_quantity
            sold_items[purchase_row.id] = [purchase_row.remaining_quantity, purchase_row.rate]
            purchase_row.remaining_quantity = 0
            purchase_row.save()
    return sold_items


def handle_quantity_decrease(db_row, row, diff):
    # import ipdb; ipdb.set_trace()
    diff = abs(diff)
    r_diff = db_row.remaining_quantity - diff
    row["remaining_quantity"] = r_diff if r_diff > 0 else 0
    db_row.remaining_quantity = r_diff

    sales_rows = SalesVoucherRow.objects.filter(sold_items__has_key=str(row.get("id"))).order_by("-id")
    for sales_row in sales_rows:
        sold_items = sales_row.sold_items
        sold_quantity = sold_items[str(row["id"])][0]
        if sold_quantity > diff:
            sold_quantity -= diff
            sold_items[str(row["id"])] = [sold_quantity, sold_items[str(row["id"])][1]]
            purchase_rows = PurchaseVoucherRow.objects.filter(item_id=sales_row.item_id, remaining_quantity__gt=0).order_by("voucher__date", "id")
            for purchase_row in purchase_rows:
                if purchase_row.remaining_quantity == diff:
                    purchase_row.remaining_quantity = 0
                    purchase_row.save()
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += diff
                    else:
                        sold_items[str(purchase_row.id)] = diff
                    break
                elif purchase_row.remaining_quantity > diff:
                    purchase_row.remaining_quantity -= diff
                    purchase_row.save()
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += diff
                    else:
                        sold_items[str(purchase_row.id)] = diff
                    break
                else:
                    diff -= purchase_row.remaining_quantity
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += purchase_row.remaining_quantity
                    else:
                        sold_items[str(purchase_row.id)] = purchase_row.remaining_quantity
                    purchase_row.remaining_quantity = 0
                    purchase_row.save()
            sales_row.sold_items = sold_items
            sales_row.save()
            break
        else:
            sold_quantity = sold_items.pop(str(row["id"]))
            qt = diff - sold_quantity
            sold_items[str(row["id"])] = qt
            purchase_rows = PurchaseVoucherRow.objects.filter(item_id=sales_row.item_id, remaining_quantity__gt=0).order_by("voucher__date", "id")
            for purchase_row in purchase_rows:
                if purchase_row.remaining_quantity == diff:
                    purchase_row.remaining_quantity = 0
                    purchase_row.save()
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += diff
                    else:
                        sold_items[str(purchase_row.id)] = diff
                    break
                elif purchase_row.remaining_quantity > diff:
                    purchase_row.remaining_quantity -= diff
                    purchase_row.save()
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += diff
                    else:
                        sold_items[str(purchase_row.id)] = diff
                    break
                else:
                    diff -= purchase_row.remaining_quantity
                    if str(purchase_row.id) in sold_items.keys():
                        sold_items[str(purchase_row.id)] += purchase_row.remaining_quantity
                    else:
                        sold_items[str(purchase_row.id)] = purchase_row.remaining_quantity
                    purchase_row.remaining_quantity = 0
                    purchase_row.save()
            sales_row.sold_items = sold_items
            sales_row.save()


def fifo_handle_purchase_update(voucher, row):
    item = Item.objects.get(id=row["item_id"])
    if item.track_inventory:
        if row.get("id"):
            db_row = voucher.rows.get(id=row["id"])
            diff = row["quantity"] - db_row.quantity
            if diff >= 0:
                row["remaining_quantity"] = db_row.remaining_quantity + diff
            else:
                handle_quantity_decrease(db_row, row, diff)
        else:
            row["remaining_quantity"] = row["quantity"]
    return row
