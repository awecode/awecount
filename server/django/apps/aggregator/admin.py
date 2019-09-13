from django.contrib import admin

from .models import Widget


class WidgetAdmin(admin.ModelAdmin):
    list_filter = ('user__company', 'display_type', 'widget')
    list_display = ('name', 'widget', 'order', 'day_count', 'display_type')
    search_fields = ('name',)


admin.site.register(Widget, WidgetAdmin)
