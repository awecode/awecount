from django.contrib import admin

from apps.product.models import Item, Unit, Category


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_display = ('code', 'name', 'cost_price', 'selling_price')


class UnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'company__name')
    list_filter = ('company', 'default_unit', 'default_tax_scheme')


admin.site.register(Category, CategoryAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(Unit)
