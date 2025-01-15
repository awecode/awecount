from django.contrib import admin

from .models import Widget


class WidgetAdmin(admin.ModelAdmin):
    list_filter = ("display_type", "widget", "user")
    list_display = (
        "name",
        "widget",
        "order",
        "count",
        "group_by",
        "display_type",
        "is_active",
    )
    search_fields = ("name",)


admin.site.register(Widget, WidgetAdmin)
