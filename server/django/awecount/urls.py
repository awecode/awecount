from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls.static import static

from apps.product.views import book_by_isbn
from awecount.utils.JWTCustomAuthentication import obtain_jwt_token_custom, TokenObtainPairView
from apps.ledger import api as ledger
from apps.product import api as item
from apps.tax import api as tax
from apps.voucher import api as voucher
from apps.bank import api as bank
from apps.aggregator import api as aggregator

from apps.aggregator import views as aggregator_views

router = DefaultRouter()

# TODO fix singular/plural
router.register('parties', ledger.PartyViewSet, base_name='parties')
router.register('categories', ledger.CategoryViewSet, base_name='categories')
router.register('accounts', ledger.AccountViewSet, base_name='accounts')
router.register('inventory-account', item.InventoryAccountViewSet, base_name='inventory-account')
router.register('items', item.ItemViewSet, base_name='item')
router.register('books', item.BookViewSet, base_name='book')
router.register('brands', item.BrandViewSet, base_name='brands')
router.register('units', item.UnitViewSet, base_name='unit')
router.register('inventory-categories', item.InventoryCategoryViewSet, base_name='inventory-categories')
router.register('tax_scheme', tax.TaxSchemeViewSet, base_name='tax')
router.register('sales-voucher', voucher.SalesVoucherViewSet)
router.register('sales-discount', voucher.SalesDiscountViewSet, base_name='sales-discount')
router.register('purchase-vouchers', voucher.PurchaseVoucherViewSet, base_name='purchase-vouchers')
router.register('purchase-discount', voucher.PurchaseDiscountViewSet, base_name='purchase-discount')
router.register('credit-note', voucher.CreditNoteViewSet, base_name='credit-note')
router.register('debit-note', voucher.DebitNoteViewSet, base_name='debit-note')
router.register('journal-voucher', voucher.JournalVoucherViewSet)
router.register('invoice-design', voucher.InvoiceDesignViewSet)
router.register('cheque-deposits', bank.ChequeDepositViewSet, base_name='cheque-deposit')
router.register('bank-account', bank.BankAccountViewSet)
router.register('cheque-voucher', bank.ChequeVoucherViewSet, base_name='cheque-voucher')
router.register('log-entries', aggregator.LogEntryViewSet, base_name='log-entry')
router.register('sales-book', voucher.SalesBookViewSet, base_name='sales-book')
router.register('purchase-book', voucher.PurchaseBookViewSet, base_name='purchase-book')

urlpatterns = [
                  path('aweadmin/', admin.site.urls),
                  path('', include('apps.voucher.urls')),
                  re_path(r'^v1/book/isbn-api/(?P<isbn>[0-9]+?)/$', book_by_isbn, name='book-isbn-api'),
                  path('v1/', include(router.urls)),
                  path('v1/auth/', include('djoser.urls.base')),
                  path('v1/auth/', include('djoser.urls.jwt')),
                  path('v1/auth/login/', TokenObtainPairView.as_view(), name='login'),
                  path('export/', aggregator_views.export_data, name='export_data')

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
