from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

from apps.product.views import book_by_isbn
from awecount.utils.JWTCustomAuthentication import TokenObtainPairView
from apps.ledger import api as ledger
from apps.product import api as item
from apps.tax import api as tax
from apps.voucher import api as voucher
from apps.bank import api as bank
from apps.aggregator import api as aggregator

from apps.aggregator import views as aggregator_views

router = DefaultRouter()

# TODO fix singular/plural
# TODO problem with basename
router.register('parties', ledger.PartyViewSet, basename='parties')
router.register('categories', ledger.CategoryViewSet, basename='categories')
router.register('accounts', ledger.AccountViewSet, basename='accounts')

router.register('inventory-account', item.InventoryAccountViewSet, basename='inventory-account')
router.register('account-opening-balance', ledger.AccountOpeningBalanceViewSet, basename='account-opening-balance')

# item
router.register('items', item.ItemViewSet, basename='item')
router.register('books', item.BookViewSet, basename='book')
router.register('brands', item.BrandViewSet, basename='brands')
router.register('units', item.UnitViewSet, basename='unit')
router.register('inventory-categories', item.InventoryCategoryViewSet, basename='inventory-categories')

# voucher
router.register('sales-voucher', voucher.SalesVoucherViewSet)
router.register('pos', voucher.POSViewSet)
router.register('sales-discount', voucher.SalesDiscountViewSet, basename='sales-discount')
router.register('payment-receipt', voucher.PaymentReceiptViewSet, basename='payment-receipt')
router.register('purchase-vouchers', voucher.PurchaseVoucherViewSet, basename='purchase-vouchers')
router.register('purchase-discount', voucher.PurchaseDiscountViewSet, basename='purchase-discount')
router.register('purchase-settings', voucher.PurchaseSettingsViewSet, basename='purchase-settings')
router.register('credit-note', voucher.CreditNoteViewSet, basename='credit-note')
router.register('debit-note', voucher.DebitNoteViewSet, basename='debit-note')
router.register('journal-voucher', voucher.JournalVoucherViewSet)
router.register('invoice-design', voucher.InvoiceDesignViewSet)
router.register('sales-book', voucher.SalesBookViewSet, basename='sales-book')
router.register('sales-row', voucher.SalesRowViewSet, basename='sales-row')
router.register('sales-agent', voucher.SalesAgentViewSet, basename='sales-agent')
router.register('sales-settings', voucher.SalesSettingsViewSet, basename='sales-settings')
router.register('purchase-book', voucher.PurchaseBookViewSet, basename='purchase-book')

# bank
router.register('cheque-deposits', bank.ChequeDepositViewSet, basename='cheque-deposit')
router.register('bank-account', bank.BankAccountViewSet)
router.register('cheque-issue', bank.ChequeIssueViewSet, basename='cheque-issue')

# tax
router.register('tax_scheme', tax.TaxSchemeViewSet, basename='tax')
router.register('tax-payments', tax.TaxPaymentViewSet, basename='tax-payment')

# aggregator
router.register('log-entries', aggregator.LogEntryViewSet, basename='log-entry')
router.register('widgets', aggregator.WidgetViewSet, basename='widget')

urlpatterns = [
                  path('aweadmin/', admin.site.urls),
                  path('', include('apps.voucher.urls')),
                  re_path(r'^v1/book/isbn-api/(?P<isbn>[0-9]+?)/$', book_by_isbn, name='book-isbn-api'),
                  path('v1/', include(router.urls)),
                  path('v1/auth/', include('djoser.urls.base')),
                  path('v1/auth/', include('djoser.urls.jwt')),
                  path('v1/auth/login/', TokenObtainPairView.as_view(), name='login'),
                  path('v1/export/', aggregator_views.export_data, name='export_data'),
                  path('v1/export/auditlog/', aggregator_views.export_auditlog, name='export_auditlog'),
                  path('v1/import/', aggregator_views.import_data, name='import_data'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
