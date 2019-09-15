from apps.aggregator.base_widgets import BaseWidget
from apps.voucher.models import SalesVoucher


class SalesCountWidget(BaseWidget):
    def get_base_queryset(self):
        return SalesVoucher.objects.all()


class SalesCountByAgent(SalesCountWidget):
    name = 'Sales Count by Agent'
    label_field = 'sales_agent__name'
    table_headings = ['Sales Agent', 'Sales Count']


class SalesCountByParty(SalesCountWidget):
    name = 'Sales Count by Party'
    label_field = 'party__name'


class SalesAmountWidget(BaseWidget):
    sum_field = 'total_amount'

    def get_base_queryset(self):
        return SalesVoucher.objects.all()


class SalesAmountByAgent(SalesAmountWidget):
    name = 'Sales Amount by Agent'
    label_field = 'sales_agent__name'
    table_headings = ['Sales Agent', 'Amount']


class SalesAmountByParty(SalesAmountWidget):
    name = 'Sales Amount by Party'
    label_field = 'party__name'


WIDGETS = [SalesAmountByParty, SalesAmountByAgent, SalesCountByAgent, SalesCountByParty]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
