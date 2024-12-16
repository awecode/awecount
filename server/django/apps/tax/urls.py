from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tax import api as tax

router = DefaultRouter()


router.register("tax_scheme", tax.TaxSchemeViewSet, basename="tax")
router.register("tax-payments", tax.TaxPaymentViewSet, basename="tax-payment")


urlpatterns = [
    path("v1/", include(router.urls)),
]
