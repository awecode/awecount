import requests
from django.contrib import admin, messages
from django.db import models, transaction

from apps.product.models import (
    BillOfMaterial,
    Brand,
    Category,
    InventoryAccount,
    InventoryAdjustmentVoucher,
    InventoryConversionVoucher,
    InventorySetting,
    Item,
    JournalEntry,
    Transaction,
    Unit,
)


def merge_brands(modeladmin, request, queryset):
    count = len(queryset)
    if count < 2:
        messages.warning(request, "Select at least two brands.")
    else:
        first_brand = queryset[0]
        for brand in queryset[1:]:
            Item.objects.filter(brand=brand).update(brand=first_brand)
            brand.delete()
        messages.success(request, "Merged {} brands".format(count))


merge_brands.short_description = "Merge brands"


def delete_item_data(modeladmin, request, queryset):
    count = len(queryset)
    if count > 1:
        messages.warning(request, "Please select only one item.")
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
                messages.success(request, "Deleted items!".format())
        except models.ProtectedError:
            messages.error(request, "Cannot delete! Transactions exist.".format())


delete_item_data.short_description = "Delete Full Item Data"


def fix_book_title(modeladmin, request, queryset):
    saved_cnt = 0
    skipped_cnt = 0
    for item in queryset:
        url = "https://tbe.thuprai.com/v1/book/isbn/{}/".format(item.code)
        response = requests.get(url)
        if response.ok:
            book_detail = response.json()
            if book_detail.get("english_title"):
                item.name = book_detail.get("english_title")
                item.save()
                saved_cnt += 1
            else:
                skipped_cnt += 1
        else:
            skipped_cnt += 1
    messages.warning(
        request, "Saved {} items, skipped {} items".format(saved_cnt, skipped_cnt)
    )


fix_book_title.short_description = "Fix book title to English"

admin.site.register(JournalEntry)
admin.site.register(InventorySetting)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "short_name",
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ("name", "description")
    list_filter = ("company",)
    actions = [merge_brands]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name", "company__name")
    list_filter = (
        "track_inventory",
        "can_be_sold",
        "can_be_purchased",
        "fixed_asset",
        "direct_expense",
        "indirect_expense",
    )
    autocomplete_fields = (
        "company",
        "default_unit",
        "default_tax_scheme",
        "sales_account",
        "purchase_account",
        "discount_allowed_account",
        "discount_received_account",
        "sales_account_category",
        "purchase_account_category",
        "discount_allowed_account_category",
        "discount_received_account_category",
        "fixed_asset_account_category",
        "direct_expense_account_category",
        "indirect_expense_account_category",
        "dedicated_sales_account",
        "dedicated_purchase_account",
        "dedicated_discount_allowed_account",
        "dedicated_discount_received_account",
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ("name", "code", "description", "selling_price", "cost_price")
    list_filter = (
        "track_inventory",
        "can_be_sold",
        "can_be_purchased",
        "fixed_asset",
        "direct_expense",
        "indirect_expense",
        "company",
    )
    list_display = ("code", "name", "cost_price", "selling_price", "brand")
    actions = (delete_item_data, fix_book_title)
    readonly_fields = (
        "account",
        "sales_account",
        "expense_account",
        "purchase_account",
        "fixed_asset_account",
        "discount_allowed_account",
        "discount_received_account",
    )
    autocomplete_fields = (
        "brand",
        "unit",
        "company",
        "category",
        "tax_scheme",
        "dedicated_sales_account",
        "dedicated_purchase_account",
        "dedicated_discount_allowed_account",
        "dedicated_discount_received_account",
    )


@admin.register(InventoryAccount)
class InventoryAccountAdmin(admin.ModelAdmin):
    search_fields = ("code", "name", "account_no")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    raw_id_fields = ("journal_entry",)


admin.site.register(BillOfMaterial)


class InventoryAdjustmentVoucherAdmin(admin.ModelAdmin):
    search_fields = (
        "voucher_no",
        "company__name",
    )
    list_filter = ("company",)
    list_display = ("voucher_no",)


admin.site.register(InventoryAdjustmentVoucher, InventoryAdjustmentVoucherAdmin)


admin.site.register(InventoryConversionVoucher)
