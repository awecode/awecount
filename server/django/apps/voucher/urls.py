from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.voucher import api as voucher
from apps.voucher.api import partner as partner_voucher
from apps.voucher.api.payment_mode import PaymentModeViewSet

from . import views

router = SimpleRouter()

router.register("payment-modes", PaymentModeViewSet, basename="payment-modes")


router.register(
    "partner/purchase-voucher",
    partner_voucher.PartnerPurchaseVoucherViewSet,
    basename="partner-purchase-voucher",
)

router.register(
    "partner/purchase-discount",
    partner_voucher.PartnerPurchaseDiscountViewSet,
    basename="partner-purchase-discount",
)

router.register(
    "partner/credit-note",
    partner_voucher.PartnerCreditNoteViewSet,
    basename="partner-credit-note",
)

router.register(
    "partner/debit-note",
    partner_voucher.PartnerDebitNoteViewSet,
    basename="partner-debit-note",
)


# voucher
router.register("sales-voucher", voucher.SalesVoucherViewSet)
router.register("pos", voucher.POSViewSet, basename="pos")
router.register(
    "sales-discount", voucher.SalesDiscountViewSet, basename="sales-discount"
)
router.register(
    "payment-receipt", voucher.PaymentReceiptViewSet, basename="payment-receipt"
)
router.register(
    "purchase-vouchers", voucher.PurchaseVoucherViewSet, basename="purchase-vouchers"
)
router.register(
    "purchase-voucher-row",
    voucher.PurchaseVoucherRowViewSet,
    basename="purchase-voucher-row",
)
router.register(
    "purchase-discount", voucher.PurchaseDiscountViewSet, basename="purchase-discount"
)
router.register(
    "purchase-settings", voucher.PurchaseSettingsViewSet, basename="purchase-settings"
)
router.register("credit-note", voucher.CreditNoteViewSet, basename="credit-note")
router.register("debit-note", voucher.DebitNoteViewSet, basename="debit-note")
router.register("challan", voucher.ChallanViewSet, basename="challan")
router.register("journal-voucher", voucher.JournalVoucherViewSet)
router.register("invoice-design", voucher.InvoiceDesignViewSet)
router.register("sales-book", voucher.SalesBookViewSet, basename="sales-book")
router.register("sales-row", voucher.SalesRowViewSet, basename="sales-row")
router.register("sales-agent", voucher.SalesAgentViewSet, basename="sales-agent")

router.register(
    "sales-settings", voucher.SalesSettingsViewSet, basename="sales-settings"
)

router.register("purchase-book", voucher.PurchaseBookViewSet, basename="purchase-book")
router.register(
    "purchase-order", voucher.PurchaseOrderViewSet, basename="purchase-order"
)

router.register("recurring-voucher-template", voucher.RecurringVoucherTemplateViewSet, basename="recurring-voucher-template")


urlpatterns = [
    path("api/company/<slug:company_slug>/upload-file/", views.FileUploadView.as_view(), name="upload-file"),
    path("api/company/<slug:company_slug>/invoice-setting-update/", views.InvoiceSettingUpdateView.as_view()),
    path("api/company/<slug:company_slug>/", include(router.urls)),
]
