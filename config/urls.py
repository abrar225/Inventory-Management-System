"""Root URL configuration for the Inventory Management System.

Domain apps own their own ``urls.py`` and are included here under stable
namespaces as each phase lands. In Phase 1 only the foundation home page and
the Django admin are wired; authentication, dashboard, and business modules
are added in their respective phases.

Media files are served by Django only in development; in production WhiteNoise
serves static assets and media is served by the web server / storage backend.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("catalog/", include("apps.catalog.urls", namespace="catalog")),
    path("inventory/", include("apps.inventory.urls", namespace="inventory")),
    path("purchasing/", include("apps.purchasing.urls", namespace="purchasing")),
    path("sales/", include("apps.sales.urls", namespace="sales")),
    path("reports/", include("apps.reporting.urls", namespace="reporting")),
    path("audit/", include("apps.audit.urls", namespace="audit")),
    path("", include("apps.common.urls")),
]

# Custom error handlers (templates live in templates/errors/).
handler403 = "apps.common.views.handler403"
handler404 = "apps.common.views.handler404"
handler500 = "apps.common.views.handler500"

if settings.DEBUG:
    urlpatterns += static(  # type: ignore[arg-type]
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
