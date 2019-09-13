import datetime
from django.db.models import Count

from apps.voucher.models import SalesVoucher


class BaseWidget(object):
    date_attribute = 'date'
    data_field = 'cnt'

    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'name'):
            raise NotImplementedError("Widgets must specify 'name' attribute!")
        self.instance = kwargs.get('instance')
        self.company_id = self.instance.user.company_id
        self.type = self.instance.display_type
        self.days = self.instance.day_count
        self.labels = []
        self.datasets = []
        self.values = []
        self.date_indices = {}

    def is_series(self):
        return self.type.lower() not in ['pie', 'percentage', 'table']

    def is_table(self):
        return self.type == 'Table'

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

    def get_date_labels(self):
        labels = []
        for i in range(0, self.days):
            sub_date = self.end_date - datetime.timedelta(days=(self.days - i - 1))
            labels.append(sub_date)
            self.date_indices[sub_date] = i
        return labels

    def __str__(self):
        return self.name

    # def get_data(self):
    #     return self.get_queryset()

    def get_data(self):
        data = self.get_queryset()
        if self.is_table():
            self.datasets = data
        elif self.is_series():
            self.labels = self.get_date_labels()
            dct = {}
            for datum in data:
                if not datum[self.label_field] in dct.keys():
                    dct[datum[self.label_field]] = [0] * self.days
                dct[datum[self.label_field]][self.date_indices[datum[self.date_attribute]]] = datum['cnt']

            for key, val in dct.items():
                self.datasets.append({'name': key, 'values': val})
        else:
            for datum in data:
                self.labels.append(datum.get(self.label_field) or 'None')
                self.values.append(datum.get(self.data_field))
            self.datasets = [{'values': self.values}]
        return {
            'type': self.type,
            'labels': self.labels,
            'datasets': self.datasets,
        }

    def get_base_queryset(self):
        if self.is_series():
            return self.get_series_queryset()
        else:
            return self.get_nonseries_queryset()


class SalesCountWidget(BaseWidget):
    def get_nonseries_queryset(self):
        return SalesVoucher.objects.values(self.label_field).order_by(self.label_field).annotate(
            cnt=Count(self.label_field))

    def get_series_queryset(self):
        return SalesVoucher.objects.values(self.label_field, self.date_attribute).order_by(self.label_field,
                                                                                           self.date_attribute).annotate(
            cnt=Count(self.label_field))


class SalesCountByAgent(SalesCountWidget):
    name = 'Sales Count by Agent'
    label_field = 'sales_agent__name'


class SalesCountByParty(SalesCountWidget):
    name = 'Sales Count by Party'
    label_field = 'party__name'


WIDGETS = [SalesCountByAgent, SalesCountByParty, ]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
