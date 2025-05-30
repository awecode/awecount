from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from apps.product import api as item
from apps.product.api import partner as partner_item

router = SimpleRouter()


router.register(
    "inventory-account", item.InventoryAccountViewSet, basename="inventory-account"
)


# item
router.register("items", item.ItemViewSet, basename="item")
router.register("books", item.BookViewSet, basename="book")
router.register("brands", item.BrandViewSet, basename="brands")
router.register("units", item.UnitViewSet, basename="unit")
router.register(
    "inventory-categories",
    item.InventoryCategoryViewSet,
    basename="inventory-categories",
)
router.register(
    "item-opening-balance",
    item.ItemOpeningBalanceViewSet,
    basename="item-opening-balance",
)
router.register(
    "bill-of-material",
    item.BillOfMaterialViewSet,
    basename="bill-of-material",
)

router.register(
    "partner/item", partner_item.PartnerItemViewSet, basename="partner-item"
)


router.register(
    "inventory-adjustment",
    item.InventoryAdjustmentVoucherViewSet,
    basename="inventory-adjustment",
)
router.register(
    "inventory-conversion",
    item.InventoryConversionVoucherViewSet,
    basename="inventory-conversion",
)

router.register(
    "inventory-settings", item.InventorySettingsViewSet, basename="inventory-settings"
)


urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
