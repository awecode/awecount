from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.api.views import APIKeyViewSet


router = SimpleRouter()
router.register(r"api-tokens", APIKeyViewSet, basename="api-tokens")

urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
