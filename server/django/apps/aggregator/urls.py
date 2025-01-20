from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.aggregator import api as aggregator
from apps.aggregator import views as aggregator_views

router = SimpleRouter()

router.register("log-entries", aggregator.LogEntryViewSet, basename="log-entry")
router.register("widgets", aggregator.WidgetViewSet, basename="widget")

urlpatterns = [
    path(
        "api/company/<slug:company_slug>/",
        include(router.urls),
    ),
    path(
        "api/company/<slug:company_slug>/export/",
        aggregator_views.export_data,
        name="export_data",
    ),
    path(
        "api/company/<slug:company_slug>/export/auditlog/",
        aggregator_views.export_auditlog,
        name="export_auditlog",
    ),
    path(
        "api/company/<slug:company_slug>/import/",
        aggregator_views.import_data,
        name="import_data",
    ),
]
