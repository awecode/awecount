from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.bank import api as bank

router = SimpleRouter()

router.register("cheque-deposits", bank.ChequeDepositViewSet, basename="cheque-deposit")
router.register("bank-cash-deposits", bank.CashDepositViewSet, basename="cash-deposit")
router.register("bank-account", bank.BankAccountViewSet)
router.register("cheque-issue", bank.ChequeIssueViewSet, basename="cheque-issue")
router.register("fund-transfer", bank.FundTransferViewSet, basename="fund-transfer")
router.register("bank-reconciliation", bank.ReconciliationViewSet, basename="bank-reconciliation")


urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
