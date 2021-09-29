from django.contrib import admin, messages

from apps.product.models import Item, Unit, Category, JournalEntry, Transaction, InventoryAccount, Brand


def merge_brands(modeladmin, request, queryset):
    count = len(queryset)
    if count < 2:
        messages.warning(request, 'Select at least two brands.')
    else:
        first_brand = queryset[0]
        for brand in queryset[1:]:
            Item.objects.filter(brand=brand).update(brand=first_brand)
            brand.delete()
        messages.success(request, 'Merged {} brands'.format(count))


merge_brands.short_description = "Merge brands"


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_filter = (
        'track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense', 'brand')
    list_display = ('code', 'name', 'cost_price', 'selling_price', 'brand')


class UnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'company__name')
    list_filter = ('track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense')


admin.site.register(Category, CategoryAdmin)


class InventoryAccountAdmin(admin.ModelAdmin):
    search_fields = ('adhunikalochana', 'Adhunik Alochana Anek Rup')


admin.site.register(Item, ItemAdmin)
admin.site.register(InventoryAccount, InventoryAccountAdmin)
admin.site.register(JournalEntry)
admin.site.register(Transaction)
admin.site.register(Unit)


class BrandAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_filter = ('company',)
    actions = [merge_brands, ]


admin.site.register(Brand, BrandAdmin)
