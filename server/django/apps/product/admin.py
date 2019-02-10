from django.contrib import admin

from apps.product.models import Item


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_display = ('code', 'name', 'cost_price', 'selling_price')


admin.site.register(Item, ItemAdmin)
