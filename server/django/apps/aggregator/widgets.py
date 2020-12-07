from functools import reduce

from apps.aggregator.base_widgets import BaseWidget
from apps.voucher.models import SalesVoucher, PurchaseVoucher


class SalesCountWidget(BaseWidget):
    def get_base_queryset(self):
        return SalesVoucher.objects.exclude(status__in=['Draft', 'Cancelled'])


class PurchaseCountWidget(BaseWidget):
    def get_base_queryset(self):
        return PurchaseVoucher.objects.exclude(status__in=['Draft', 'Cancelled'])


class SalesCountByAgent(SalesCountWidget):
    name = 'Sales Count by Agent'
    label_field = 'sales_agent__name'
    table_headings = ['Sales Agent', 'Sales Count']


class SalesCountByParty(SalesCountWidget):
    name = 'Sales Count by Party'
    label_field = 'party__name'


class SalesCountByMode(SalesCountWidget):
    name = "Sales Count by Mode"
    label_field = 'mode'


class PurchaseCountByMode(PurchaseCountWidget):
    name = "Purchase Count by Mode"
    label_field = 'mode'


class SalesAmountWidget(BaseWidget):
    sum_field = 'total_amount'

    def get_base_queryset(self):
        return SalesVoucher.objects.exclude(status__in=['Draft', 'Cancelled'])


class SalesAmountByAgent(SalesAmountWidget):
    name = 'Sales Amount by Agent'
    label_field = 'sales_agent__name'
    table_headings = ['Sales Agent', 'Amount']


class SalesAmountByParty(SalesAmountWidget):
    name = 'Sales Amount by Party'
    label_field = 'party__name'


class PurchaseAmountWidget(BaseWidget):
    sum_field = 'total_amount'

    def get_base_queryset(self):
        return PurchaseVoucher.objects.exclude(status__in=['Draft', 'Cancelled'])


class TotalPurchaseAmount(PurchaseAmountWidget):
    name = "Total Purchase Amount"
    label_field = 'date'
    series = False


class TotalSalesAmount(SalesAmountWidget):
    name = "Total Sales Amount"
    label_field = 'date'
    series = False


class PurchaseCountByParty(PurchaseCountWidget):
    name = "Purchase Count by Party"
    label_field = 'party__name'


WIDGETS = [SalesAmountByParty, SalesAmountByAgent, SalesCountByAgent, SalesCountByParty, PurchaseCountByParty,
           TotalPurchaseAmount, TotalSalesAmount, SalesCountByMode, PurchaseCountByMode]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
