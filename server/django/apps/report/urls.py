from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.report import api as report_api

router = SimpleRouter()

# Report
router.register("report", report_api.ReportViewSet, basename="report")


urlpatterns = [
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
]
