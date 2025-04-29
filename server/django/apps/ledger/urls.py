from django.urls import include, re_path
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
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/",
        include(router.urls),
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/category-tree/$",
        ledger.CategoryTreeView.as_view(),
        name="category-tree",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/full-category-tree/$",
        ledger.FullCategoryTreeView.as_view(),
        name="full-category-tree",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/trial-balance/$",
        ledger.TrialBalanceView.as_view(),
        name="trial-balance",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/balance-sheet/$",
        ledger.BalanceSheetView.as_view(),
        name="balance-sheet",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/income-statement/$",
        ledger.IncomeStatementView.as_view(),
        name="income-statement",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/tax-summary/$",
        ledger.TaxSummaryView.as_view(),
        name="tax-summary",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/customer-closing-summary/$",
        ledger.CustomerClosingView.as_view(),
        name="customer-closing-summary",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/chart-of-accounts/$",
        ledger.ChartOfAccountsView.as_view(),
        name="chart-of-accounts",
    ),

]
