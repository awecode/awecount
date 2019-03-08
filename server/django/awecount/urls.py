from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls.static import static

from awecount.utils.JWTCustomAuthentication import obtain_jwt_token_custom, TokenObtainPairView
from apps.ledger import api as ledger
from apps.product import api as item
from apps.tax import api as tax
from apps.voucher import api as voucher

router = DefaultRouter()

router.register('parties', ledger.PartyViewSet, base_name='parties')
router.register('accounts', ledger.AccountViewSet)
router.register('items', item.ItemViewSet, base_name='item')
router.register('tax_scheme', tax.TaxSchemeViewSet, base_name='tax')
router.register('sale-voucher', voucher.SalesVoucherViewSet)
router.register('credit-voucher', voucher.CreditVoucherViewSet)
router.register('cheque-voucher', voucher.ChequeVoucherViewSet, base_name='chequevoucher')
router.register('bank-branch', voucher.BankBranchViewSet, base_name='bankbranch')
router.register('invoice-design', voucher.InvoiceDesignViewSet)

urlpatterns = [
    path('aweadmin/', admin.site.urls),
    path('v1/', include(router.urls)),
    path('v1/auth/', include('djoser.urls.base')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/auth/login/',TokenObtainPairView.as_view(), name='login')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
