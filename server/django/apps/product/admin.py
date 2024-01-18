import requests
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import ProtectedError

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
        try:
            with transaction.atomic():
                item.account and item.account.delete()
                item.sales_account and item.sales_account.delete()
                item.purchase_account and item.purchase_account.delete()
                item.discount_allowed_account and item.discount_allowed_account.delete()
                item.discount_received_account and item.discount_received_account.delete()
                item.expense_account and item.expense_account.delete()
                item.fixed_asset_account and item.fixed_asset_account.delete()
                item.delete()
                messages.success(request, 'Deleted items!'.format(count))
        except ProtectedError:
            messages.error(request, 'Cannot delete! Transactions exist.'.format(count))


delete_item_data.short_description = "Delete Full Item Data"


def fix_book_title(modeladmin, request, queryset):
    saved_cnt = 0
    skipped_cnt = 0
    for item in queryset:
        url = 'https://tbe.thuprai.com/v1/book/isbn/{}/'.format(item.code)
        response = requests.get(url)
        if response.ok:
            book_detail = response.json()
            if book_detail.get('english_title'):
                item.name = book_detail.get('english_title')
                item.save()
                saved_cnt += 1
            else:
                skipped_cnt += 1
        else:
            skipped_cnt += 1
    messages.warning(request, 'Saved {} items, skipped {} items'.format(saved_cnt, skipped_cnt))


fix_book_title.short_description = "Fix book title to English"


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code', 'description', 'selling_price', 'cost_price')
    list_filter = (
        'track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense',
        'company')
    list_display = ('code', 'name', 'cost_price', 'selling_price', 'brand')
    actions = (delete_item_data, fix_book_title)
    readonly_fields = (
        'account', 'sales_account', 'purchase_account', 'discount_allowed_account', 'discount_received_account',
        'expense_account', 'fixed_asset_account')


class UnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'company__name')
    list_filter = (
        'track_inventory', 'can_be_sold', 'can_be_purchased', 'fixed_asset', 'direct_expense', 'indirect_expense')


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
