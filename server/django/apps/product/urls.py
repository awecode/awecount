from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.ledger import api as ledger
from apps.ledger.api import partner as partner_ledger

router = DefaultRouter()


router.register("parties", ledger.PartyViewSet, basename="parties")
router.register("categories", ledger.CategoryViewSet, basename="categories")
router.register("accounts", ledger.AccountViewSet, basename="accounts")

router.register(
    "partner/journal-voucher",
    partner_ledger.PartnerJournalVoucherViewSet,
    basename="partner-journal-voucher",
)
router.register(
    "partner/party",
    partner_ledger.PartnerPartyViewSet,
    basename="partner-party",
)
router.register(
    "partner/sales-voucher",
    partner_ledger.PartnerSalesVoucherViewSet,
    basename="partner-sales-voucher",
)

router.register(
    "account-opening-balance",
    ledger.AccountOpeningBalanceViewSet,
    basename="account-opening-balance",
)
router.register("transaction", ledger.TransactionViewSet, basename="transaction")

router.register(
    "account-closing", ledger.AccountClosingViewSet, basename="account-closing"
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/category-tree/", ledger.CategoryTreeView.as_view(), name="category-tree"),
    path(
        "v1/full-category-tree/",
        ledger.FullCategoryTreeView.as_view(),
        name="full-category-tree",
    ),
    path("v1/trial-balance/", ledger.TrialBalanceView.as_view(), name="trial-balance"),
    path("v1/tax-summary/", ledger.TaxSummaryView.as_view(), name="tax-summary"),
    path(
        "v1/customer-closing-summary/",
        ledger.CustomerClosingView.as_view(),
        name="customer-closing-summary",
    ),
]
