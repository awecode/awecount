from django.db.models import Sum

from apps.aggregator.base_widgets import BaseWidget
from apps.voucher.models import SalesVoucher


class SalesCountWidget(BaseWidget):
    def get_base_queryset(self):
        return SalesVoucher.objects.all()


class SalesCountByAgent(SalesCountWidget):
    name = 'Sales Count by Agent'
    label_field = 'sales_agent__name'


class SalesCountByParty(SalesCountWidget):
    name = 'Sales Count by Party'
    label_field = 'party__name'


class SalesAmountWidget(BaseWidget):
    data_field = 'sum'

    def get_base_queryset(self):
        return SalesVoucher.objects.all()

    def annotate(self, qs):
        return qs.annotate(sum=Sum('total_amount'))


class SalesAmountByAgent(SalesAmountWidget):
    name = 'Sales Amount by Agent'
    label_field = 'sales_agent__name'


class SalesAmountByParty(SalesAmountWidget):
    name = 'Sales Amount by Party'
    label_field = 'party__name'


WIDGETS = [SalesAmountByParty, SalesAmountByAgent, SalesCountByAgent, SalesCountByParty]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
