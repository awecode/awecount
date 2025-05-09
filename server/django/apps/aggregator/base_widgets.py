import datetime
import time

from dateutil.rrule import MONTHLY, WEEKLY, YEARLY, rrule
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractWeek, ExtractYear


class BaseWidget(object):
    date_attribute = "date"
    data_field = "cnt"
    sum_field = None
    table_headings = []
    series = True

    # By defaults, processes count of `label_field`
    # Set `sum_field` to process sum

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "name"):
            raise NotImplementedError("Widgets must specify 'name' attribute!")

        self.instance = kwargs.get("instance")
        self.company_id = self.instance.user.company_id
        self.type = self.instance.display_type
        self.group_by = self.instance.group_by.lower()
        if self.group_by == "day":
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

        if self.sum_field:
            self.data_field = "sum"

    def is_series(self):
        return self.series and self.type.lower() not in [
            "table",
            "pie",
            "percentage",
            "doughnut",
            "polar area",
        ]

    def is_table(self):
        return self.type == "Table"

    def get_start_date(self, delta, count):
        year = self.today.year
        month = self.today.month
        day = self.today.day
        if delta == "year":
            year = year - count + 1
            month = 1
            day = 1
        elif delta == "month":
            month = month - count + 1
            day = 1
        elif delta == "week":
            day = day - count * 7 + 1
        if delta in ["day", "date"]:
            day = day - count
        timestamp = time.mktime((year, month, day, 0, 0, 0, 0, 0, 0))
        return datetime.datetime.fromtimestamp(timestamp)

    def get_base_queryset(self):
        if not hasattr(self, "queryset"):
            raise NotImplementedError(
                "Either implement 'queryset' attribute or a get_base_queryset method."
            )
        return self.queryset

    def get_date_labels(self):
        labels = []
        self.group_indices = {}
        if self.group_by == self.date_attribute:
            for i in range(0, self.count + 1):
                sub_date = self.end_date - datetime.timedelta(days=(self.count - i))
                labels.append(sub_date)
                self.group_indices[sub_date] = i
        elif self.group_by == "month":
            dates = [
                dt
                for dt in rrule(MONTHLY, dtstart=self.start_date, until=self.end_date)
            ]
            for idx, date in enumerate(dates):
                self.group_indices[date.month] = idx
                labels.append(date.strftime("%B"))
        elif self.group_by == "week":
            dates = [
                dt for dt in rrule(WEEKLY, dtstart=self.start_date, until=self.end_date)
            ]

            # Add current week if not in dates
            today = datetime.date.today()
            weeks = [dt.isocalendar().week for dt in dates]
            if today.isocalendar().week not in weeks:
                dates.append(today)

            for idx, date in enumerate(dates):
                week_num = date.isocalendar()[1]
                self.group_indices[week_num] = idx
                labels.append("Week {}".format(week_num))

        elif self.group_by == "year":
            dates = [
                dt for dt in rrule(YEARLY, dtstart=self.start_date, until=self.end_date)
            ]
            for idx, date in enumerate(dates):
                self.group_indices[date.year] = idx
                labels.append(date.strftime("%Y"))

        return labels

    def __str__(self):
        return self.name

    def get_table_headings(self, data):
        dct = {}
        if data and len(data):
            for idx, key in enumerate(data[0].keys()):
                dct[key] = (
                    self.table_headings[idx]
                    if self.table_headings
                    else key.replace("__", " ")
                    .replace("_", " ")
                    .replace("cnt", "Count")
                    .title()
                )
        return dct

    def get_data(self):
        data = self.process_queryset()

        if self.is_table():
            self.datasets = data
            self.labels = self.get_table_headings(data)
        elif self.is_series():
            self.labels = self.get_date_labels()
            dct = {}
            for datum in data:
                if datum[self.label_field] not in dct.keys():
                    dct[datum[self.label_field]] = [0] * (self.count + 1)
                dct[datum[self.label_field]][
                    self.group_indices[datum[self.group_by]]
                ] = datum[self.data_field]

            for key, val in dct.items():
                self.datasets.append({"label": key or "None", "data": val})
        else:
            for datum in data:
                self.labels.append(datum.get(self.label_field) or "None")
                self.values.append(datum.get(self.data_field))
            self.datasets = [{"data": self.values, "label": ""}]
        return {
            "type": self.title_case(self.type),
            "labels": self.labels,
            "datasets": self.datasets,
        }

    def title_case(self, st):
        ret = "".join(x for x in st.title() if not x.isspace())
        return ret[0].lower() + ret[1:]

    def process_queryset(self):
        qs = self.get_queryset().filter(company_id=self.company_id)
        if hasattr(self, "values") and self.values:
            qs = qs.values(*self.values)
        if hasattr(self, "count") and self.count:
            date_kwargs = {
                self.date_attribute + "__gte": self.start_date,
                self.date_attribute + "__lte": self.end_date,
            }
            qs = qs.filter(**date_kwargs)
        return qs

    def get_queryset(self):
        if self.is_series():
            qs = self.get_series_queryset()
        else:
            qs = self.get_nonseries_queryset()
        return self.annotate(qs)

    def annotate(self, qs):
        if self.data_field == "cnt":
            return qs.annotate(cnt=Count(self.label_field))
        elif self.data_field == "sum":
            return qs.annotate(sum=Sum(self.sum_field))
        return qs

    def get_nonseries_queryset(self):
        qs = self.get_base_queryset()
        if self.date_attribute:
            if self.group_by == "month":
                qs = qs.annotate(month=ExtractMonth(self.date_attribute))
            elif self.group_by == "year":
                qs = qs.annotate(year=ExtractYear(self.date_attribute))
            elif self.group_by == "week":
                qs = qs.annotate(week=ExtractWeek(self.date_attribute))
        qs = qs.values(self.label_field).order_by(self.label_field)
        return qs

    def get_series_queryset(self):
        qs = self.get_base_queryset()
        if self.group_by == "month":
            qs = qs.annotate(month=ExtractMonth(self.date_attribute))
        elif self.group_by == "year":
            qs = qs.annotate(year=ExtractYear(self.date_attribute))
        elif self.group_by == "week":
            qs = qs.annotate(week=ExtractWeek(self.date_attribute))
        qs = qs.values(self.label_field, self.group_by).order_by(
            self.label_field, self.group_by
        )
        return qs
