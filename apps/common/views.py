"""Shared views: custom error handlers and the foundation home page.

Error handlers render the branded templates under ``templates/errors/`` with
the correct HTTP status codes. Signatures match Django's handler contract.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.defaults import ERROR_PAGE_TEMPLATE


def home(request: HttpRequest) -> HttpResponse:
    """Root route: send users to the dashboard.

    Authentication is enforced by ``LoginRequiredMiddleware``, which redirects
    anonymous users to the login page; authenticated users land on the
    dashboard.
    """
    return redirect("dashboard:index")


def handler403(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Render the 403 Forbidden page."""
    return render(request, "errors/403.html", status=403)


def handler404(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Render the 404 Not Found page."""
    return render(request, "errors/404.html", status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    """Render the 500 Server Error page.

    Falls back to Django's minimal built-in template if rendering the custom
    template itself fails, so a broken template never masks the real error.
    """
    try:
        return render(request, "errors/500.html", status=500)
    except Exception:  # pragma: no cover - defensive fallback
        from django.template import Context, Engine

        template = Engine().from_string(ERROR_PAGE_TEMPLATE)
        return HttpResponse(
            template.render(Context({})),
            status=500,
        )
