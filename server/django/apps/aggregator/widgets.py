from apps.voucher.models import SalesVoucher


class BaseWidget(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'name'):
            raise NotImplementedError("Widgets must specify 'name' attribute!")
        if not hasattr(self, 'queryset'):
            raise NotImplementedError("Widgets must specify 'queryset' attribute!")

    def get_queryset(self):
        return self.queryset.filter(company_id=self.company_id)

    def __str__(self):
        return self.name

    @property
    def data(self):
        return {'a': 1}


class SalesByAgent(BaseWidget):
    name = 'Sales By Agent'
    queryset = SalesVoucher.objects.order_by('sales_agent__name')
    # graph_types = ['pie', 'donut', 'gauge', 'bar']


WIDGETS = [SalesByAgent]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
