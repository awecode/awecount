from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.tax import api as tax

router = SimpleRouter()


router.register("tax_scheme", tax.TaxSchemeViewSet, basename="tax")
router.register("tax-payments", tax.TaxPaymentViewSet, basename="tax-payment")


urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
