from django.db.models import Count

from apps.voucher.models import SalesVoucher


class BaseWidget(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'name'):
            raise NotImplementedError("Widgets must specify 'name' attribute!")
        self.instance = kwargs.get('instance')
        self.company_id = self.instance.user.company_id

    def get_base_queryset(self):
        if not hasattr(self, 'queryset'):
            raise NotImplementedError("Either implement 'queryset' attribute or a get_base_queryset method.")
        return self.queryset

    def get_queryset(self):
        qs = self.get_base_queryset().filter(company_id=self.company_id)
        if hasattr(self, 'values') and self.values:
            qs = qs.values(*self.values)
        return qs

    def __str__(self):
        return self.name

    def get_data(self):
        return self.get_queryset()


class SalesByAgent(BaseWidget):
    name = 'Sales By Agent'

    # values = ('id', 'sales_agent__name')
    # graph_types = ['pie', 'donut', 'gauge', 'bar']

    def get_base_queryset(self):
        return SalesVoucher.objects.values('sales_agent__name').order_by('sales_agent__name').annotate(
            cnt=Count('sales_agent__name'))

    def get_data(self):
        # import ipdb
        # ipdb.set_trace()
        return self.get_queryset()


WIDGETS = [SalesByAgent]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
