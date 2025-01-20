from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.aggregator import api as aggregator
from apps.aggregator import views as aggregator_views

router = SimpleRouter()

router.register("log-entries", aggregator.LogEntryViewSet, basename="log-entry")
router.register("widgets", aggregator.WidgetViewSet, basename="widget")

urlpatterns = [
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/",
        include(router.urls),
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/export/$",
        aggregator_views.export_data,
        name="export_data",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/export/auditlog/$",
        aggregator_views.export_auditlog,
        name="export_auditlog",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/import/$",
        aggregator_views.import_data,
        name="import_data",
    ),
]
