from django.contrib import admin

from .models import Widget


class WidgetAdmin(admin.ModelAdmin):
    list_filter = ('user__company', 'display_type', 'widget')
    search_fields = ('name',)


admin.site.register(Widget, WidgetAdmin)
