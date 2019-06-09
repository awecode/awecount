from django.contrib import admin

from apps.product.models import Item, Unit


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_display = ('code', 'name', 'cost_price', 'selling_price')


class UnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name',)


admin.site.register(Item, ItemAdmin)
admin.site.register(Unit)
