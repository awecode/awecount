from django.db.models import Count

import datetime
from django.db.models import Count

from apps.voucher.models import SalesVoucher


class BaseWidget(object):
    date_attribute = 'date'
    data_field = 'cnt'
    days = 70
    date_indices = {}

    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'name'):
            raise NotImplementedError("Widgets must specify 'name' attribute!")
        self.instance = kwargs.get('instance')
        self.company_id = self.instance.user.company_id
        self.labels = []
        self.datasets = []

    @property
    def today(self):
        return datetime.date.today()

    @property
    def start_date(self):
        return self.today - datetime.timedelta(days=(self.days - 1))

    @property
    def end_date(self):
        return self.today

    def get_base_queryset(self):
        if not hasattr(self, 'queryset'):
            raise NotImplementedError("Either implement 'queryset' attribute or a get_base_queryset method.")
        return self.queryset

    def get_queryset(self):
        qs = self.get_base_queryset().filter(company_id=self.company_id)
        if hasattr(self, 'values') and self.values:
            qs = qs.values(*self.values)
        if hasattr(self, 'days') and self.days:
            date_kwargs = {self.date_attribute + '__gte': self.start_date, self.date_attribute + '__lte': self.end_date}
            qs = qs.filter(**date_kwargs)
        return qs

    def get_labels(self):
        labels = []
        for i in range(0, self.days):
            sub_date = self.end_date - datetime.timedelta(days=(self.days - i - 1))
            labels.append(sub_date)
            self.date_indices[sub_date] = i
        return labels

    def __str__(self):
        return self.name

    def get_data(self):
        return self.get_queryset()


class SalesByAgent(BaseWidget):
    name = 'Sales By Agent'
    label_field = 'sales_agent__name'

    def get_base_queryset(self):
        return SalesVoucher.objects.values(self.label_field).order_by(self.label_field).annotate(
            cnt=Count(self.label_field))

    def get_data(self):
        data = self.get_queryset()
        for datum in data:
            self.labels.append(datum.get(self.label_field) or 'None')
            self.datasets.append(datum.get(self.data_field))
        return {
            'type': 'pie',
            'labels': self.labels,
            'datasets': [{'values': self.datasets}],
        }


class DailySales(BaseWidget):
    name = 'Daily Sales by Agent'
    label_field = 'sales_agent__name'

    def get_base_queryset(self):
        return SalesVoucher.objects.values(self.label_field, self.date_attribute).order_by(self.label_field,
                                                                                           self.date_attribute).annotate(
            cnt=Count(self.label_field))

    def get_data(self):
        data = self.get_queryset()

        labels = self.get_labels()
        dct = {}
        for datum in data:
            if not datum[self.label_field] in dct.keys():
                dct[datum[self.label_field]] = [0] * self.days
            dct[datum[self.label_field]][self.date_indices[datum[self.date_attribute]]] = datum['cnt']

        for key, val in dct.items():
            self.datasets.append({'name': key, 'values': val})
        return {
            'type': 'axis-mixed',
            'labels': labels,
            'datasets': self.datasets,
        }


WIDGETS = [SalesByAgent, DailySales]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
