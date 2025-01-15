from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.bank import api as bank

router = DefaultRouter()

router.register("cheque-deposits", bank.ChequeDepositViewSet, basename="cheque-deposit")
router.register("bank-cash-deposits", bank.CashDepositViewSet, basename="cash-deposit")
router.register("bank-account", bank.BankAccountViewSet)
router.register("cheque-issue", bank.ChequeIssueViewSet, basename="cheque-issue")
router.register("fund-transfer", bank.FundTransferViewSet, basename="fund-transfer")
router.register("bank-reconciliation", bank.ReconciliationViewSet, basename="bank-reconciliation")


urlpatterns = [
    path("api/company/<slug:company_slug>/", include(router.urls)),
]
