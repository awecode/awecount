purchases = item.purchase_rows.order_by("id").values("quantity", "rate")
purchases_cumsum = purchases.annotate(cumsum=Func(Sum('quantity'), template='%(expressions)s OVER (ORDER BY %(order_by)s)', order_by="id"))
sales = item.sales_rows.order_by("id").values("quantity", "rate")
sales_cumsum = sales.annotate(cumsum=Func(Sum('quantity'), template='%(expressions)s OVER (ORDER BY %(order_by)s)', order_by="id"))
sold_qt = sales_cumsum.last()["cumsum"]
