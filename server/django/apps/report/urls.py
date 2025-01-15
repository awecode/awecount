from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.report import api as report_api

router = DefaultRouter()

# Report
router.register("report", report_api.ReportViewSet, basename="report")


urlpatterns = [
    path("api/company/<slug:company_slug>/", include(router.urls)),
]
