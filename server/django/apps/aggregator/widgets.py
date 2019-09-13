from apps.voucher.models import SalesVoucher


class BaseWidget(object):
    def __init__(self, *args, **kwargs):
        pass

    def get_queryset(self):
        return self.queryset.filter(company_id=self.company_id)
    
    
class SalesByAgent(BaseWidget):
    queryset = SalesVoucher.objects.order_by('sales_agent__name')
    # graph_types = ['pie', 'donut', 'gauge', 'bar']


WIDGETS = [
    ('Sales By Agent', SalesByAgent)
]
