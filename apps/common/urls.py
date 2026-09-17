"""URL patterns for shared/common views.

In Phase 1 this exposes the foundation home page. In development it also
exposes preview routes for the custom error pages so they can be inspected
without triggering real errors.
"""

from django.conf import settings
from django.urls import path

from . import views

app_name = "common"

urlpatterns = [
    path("", views.home, name="home"),
]

if settings.DEBUG:
    # Preview routes for error pages (development only).
    urlpatterns += [
        path("_errors/403/", views.handler403, name="preview_403"),
        path("_errors/404/", views.handler404, name="preview_404"),
        path("_errors/500/", views.handler500, name="preview_500"),
    ]
