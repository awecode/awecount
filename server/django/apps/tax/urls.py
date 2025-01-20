from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.tax import api as tax

router = SimpleRouter()


router.register("tax_scheme", tax.TaxSchemeViewSet, basename="tax")
router.register("tax-payments", tax.TaxPaymentViewSet, basename="tax-payment")


urlpatterns = [
    path("api/company/<slug:company_slug>/", include(router.urls)),
]
