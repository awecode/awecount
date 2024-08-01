SELECT * FROM product_item
WHERE company_id=1 AND id=44
ORDER BY id DESC
LIMIT 10;

SELECT id, item_id, quantity, rate, remaining_quantity
FROM voucher_purchasevoucherrow
where item_id=44
order by id;

select id, item_id, quantity, rate, sold_items
from voucher_salesvoucherrow
where item_id=44
order by id;

