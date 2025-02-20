from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin_path = "admin/" if settings.DEBUG else "aweadmin/"

urlpatterns = []

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass


urlpatterns += [
    path(admin_path, admin.site.urls),
    path("", include("apps.aggregator.urls")),
    path("", include("apps.api.urls")),
    path("", include("apps.authentication.urls")),
    path("", include("apps.bank.urls")),
    path("", include("apps.company.urls")),
    path("", include("apps.ledger.urls")),
    path("", include("apps.product.urls")),
    path("", include("apps.report.urls")),
    path("", include("apps.tax.urls")),
    path("", include("apps.users.urls")),
    path("", include("apps.voucher.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
