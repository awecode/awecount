from django.db import models

from apps.users.models import User

from .widgets import WIDGET_CHOICES, WIDGET_DICT

DISPLAY_TYPES = (
    ("Table", "Table"),
    # Series
    ("Bar", "Bar"),
    ("Line", "Line"),
    ("Radar", "Radar"),
    # #2D
    # ('Bubble', 'Bubble'),
    # #3D
    # ('Scatter', 'Scatter'),
    # Non-Series
    ("Pie", "Pie"),
    ("Doughnut", "Doughnut"),
    ("Polar Area", "Polar Area"),
    ("Mixed", "Mixed"),
)

GROUP_BY = (
    ("Day", "Day(s)"),
    ("Week", "Week(s)"),
    ("Month", "Month(s)"),
    ("Year", "Year(s)"),
)


class Widget(models.Model):
    name = models.CharField(max_length=255, blank=True)
    widget = models.CharField(choices=WIDGET_CHOICES, max_length=255)
    order = models.PositiveSmallIntegerField(default=1)
    group_by = models.CharField(choices=GROUP_BY, max_length=10, default=GROUP_BY[0][0])
    count = models.PositiveSmallIntegerField(default=7)
    display_type = models.CharField(choices=DISPLAY_TYPES, default=DISPLAY_TYPES[0][0], max_length=255)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name="widgets", on_delete=models.CASCADE)

    def get_data(self):
        Widget = self.get_widget_class()
        if Widget:
            widget = Widget(instance=self)
            return widget.get_data()

    def get_widget_class(self):
        return WIDGET_DICT.get(self.widget)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = "{} for last {} ".format(self.widget, self.count)
        self.name += self.group_by if self.count == 1 else self.group_by + "s"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-id"]
