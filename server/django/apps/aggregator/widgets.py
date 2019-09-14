import datetime
import time

from dateutil.rrule import rrule, MONTHLY

from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear

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
        self.group_by = self.instance.group_by.lower()
        if self.group_by == 'day':
            self.group_by = self.date_attribute
        self.count = self.instance.count
        self.labels = []
        self.datasets = []
        self.values = []
        self.group_indices = {}

        self.today = datetime.date.today()
        # TODO Run time check
        self.start_date = self.get_start_date(delta=self.group_by, count=self.count)
        self.end_date = self.today

    def is_series(self):
        return self.type.lower() not in ['pie', 'percentage', 'table']

    def is_table(self):
        return self.type == 'Table'

    def get_start_date(self, delta, count):
        year = self.today.year
        month = self.today.month
        day = self.today.day
        if delta == 'year':
            year = year - count + 1
            month = 1
            day = 1
        if delta == 'month':
            month = month - count + 1
            day = 1
        if delta in ['day', 'date']:
            day = day - count
        timestamp = time.mktime((year, month, day, 0, 0, 0, 0, 0, 0))
        return datetime.datetime.fromtimestamp(timestamp)

    def get_base_queryset(self):
        if not hasattr(self, 'queryset'):
            raise NotImplementedError("Either implement 'queryset' attribute or a get_base_queryset method.")
        return self.queryset

    def get_queryset(self):
        qs = self.get_base_queryset().filter(company_id=self.company_id)
        if hasattr(self, 'values') and self.values:
            qs = qs.values(*self.values)
        if hasattr(self, 'count') and self.count:
            date_kwargs = {self.date_attribute + '__gte': self.start_date, self.date_attribute + '__lte': self.end_date}
            qs = qs.filter(**date_kwargs)
        return qs

    def get_date_labels(self):
        labels = []
        if self.group_by == self.date_attribute:
            for i in range(0, self.count):
                sub_date = self.end_date - datetime.timedelta(days=(self.count - i - 1))
                labels.append(sub_date)
                self.group_indices[sub_date] = i
        elif self.group_by == 'month':
            self.group_indices = {}
            dates = [dt for dt in rrule(MONTHLY, dtstart=self.start_date, until=self.end_date)]
            for idx, date in enumerate(dates):
                self.group_indices[date.month] = idx
                labels.append(date.strftime("%B"))

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
                    dct[datum[self.label_field]] = [0] * self.count
                dct[datum[self.label_field]][self.group_indices[datum[self.group_by]]] = datum[self.data_field]

            for key, val in dct.items():
                self.datasets.append({'name': key or 'None', 'values': val})
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


class SalesAmountWidget(BaseWidget):
    data_field = 'sum'
    group_by = 'month'

    def get_nonseries_queryset(self):
        return SalesVoucher.objects.values(self.label_field).annotate(sum=Sum('total_amount'))

    def get_series_queryset(self):
        qs = SalesVoucher.objects.filter()
        qs = qs.annotate(month=ExtractMonth(self.date_attribute))
        # qs = qs.annotate(year=ExtractYear(self.date_attribute))
        qs = qs.values(self.label_field, self.group_by).order_by(self.label_field, self.group_by)
        qs = qs.annotate(sum=Sum('total_amount'))
        return qs


class SalesAmountByAgent(SalesAmountWidget):
    name = 'Sales Amount by Agent'
    label_field = 'sales_agent__name'


class SalesAmountByParty(SalesAmountWidget):
    name = 'Sales Amount by Party'
    label_field = 'party__name'


WIDGETS = [SalesAmountByParty, SalesAmountByAgent, SalesCountByAgent, SalesCountByParty]

WIDGET_CHOICES = [(widget.name, widget.name) for widget in WIDGETS]
WIDGET_DICT = {widget.name: widget for widget in WIDGETS}
