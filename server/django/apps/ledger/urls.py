from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.ledger import api as ledger
from apps.ledger.api import partner as partner_ledger

router = SimpleRouter()


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
    path(
        "api/company/<slug:company_slug>/",
        include(router.urls),
    ),
    path(
        "api/company/<slug:company_slug>/category-tree/",
        ledger.CategoryTreeView.as_view(),
        name="category-tree",
    ),
    path(
        "api/company/<slug:company_slug>/full-category-tree/",
        ledger.FullCategoryTreeView.as_view(),
        name="full-category-tree",
    ),
    path(
        "api/company/<slug:company_slug>/trial-balance/",
        ledger.TrialBalanceView.as_view(),
        name="trial-balance",
    ),
    path(
        "api/company/<slug:company_slug>/tax-summary/",
        ledger.TaxSummaryView.as_view(),
        name="tax-summary",
    ),
    path(
        "api/company/<slug:company_slug>/customer-closing-summary/",
        ledger.CustomerClosingView.as_view(),
        name="customer-closing-summary",
    ),
    path(
        "api/company/<slug:company_slug>/chart-of-accounts/",
        ledger.ChartOfAccountsView.as_view(),
        name="chart-of-accounts",
    ),

]
