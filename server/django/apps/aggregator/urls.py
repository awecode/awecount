from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.aggregator import api as aggregator
from apps.aggregator import views as aggregator_views

router = DefaultRouter()

router.register("log-entries", aggregator.LogEntryViewSet, basename="log-entry")
router.register("widgets", aggregator.WidgetViewSet, basename="widget")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/export/", aggregator_views.export_data, name="export_data"),
    path(
        "v1/export/auditlog/", aggregator_views.export_auditlog, name="export_auditlog"
    ),
    path("v1/import/", aggregator_views.import_data, name="import_data"),
]
