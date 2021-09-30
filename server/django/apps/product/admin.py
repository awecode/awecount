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


def delete_item_data(modeladmin, request, queryset):
    count = len(queryset)
    if count > 1:
        messages.warning(request, 'Please select only one item.')
    else:
        item = queryset[0]
        item.account and item.account.delete()
        item.sales_account and item.sales_account.delete()
        item.purchase_account and item.purchase_account.delete()
        item.discount_allowed_account and item.discount_allowed_account.delete()
        item.discount_received_account and item.discount_received_account.delete()
        item.expense_account and item.expense_account.delete()
        item.fixed_asset_account and item.fixed_asset_account.delete()
        item.delete()
        messages.success(request, 'Deleted items!'.format(count))


delete_item_data.short_description = "Delete Full Item Data"


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_filter = (
        'track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense', 'brand')
    list_display = ('code', 'name', 'cost_price', 'selling_price', 'brand')
    actions = (delete_item_data,)


class UnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'company__name')
    list_filter = ('track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense')


admin.site.register(Category, CategoryAdmin)


class InventoryAccountAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'account_no')


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
