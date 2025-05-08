from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.quotation import api as quotation

router = SimpleRouter()

router.register(
    "quotation-settings",
    quotation.QuotationSettingsViewSet,
    basename="quotation-settings",
)
router.register("quotation", quotation.QuotationViewSet, basename="quotation")


urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
