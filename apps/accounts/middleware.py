"""Authentication middleware.

Two concerns handled here:

* ``LoginRequiredMiddleware`` — makes authentication the default for the whole
  site, so a forgotten decorator can't silently expose a page. Views that must
  stay public are listed via ``settings.LOGIN_EXEMPT_URL_NAMES`` /
  ``LOGIN_EXEMPT_PREFIXES``. Per-view permission checks still apply on top.
* ``ActiveUserMiddleware`` — logs out a user whose account is deactivated
  during an active session, so deactivation takes effect immediately rather
  than at next login.

Rate limiting for authentication is handled at the middleware/reverse-proxy
layer per the Tech Stack and is out of scope for this module.
"""

from collections.abc import Callable

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse
from django.urls import resolve


class LoginRequiredMiddleware:
    """Require authentication for every request except exempt routes."""

    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response
        self.exempt_names = set(
            getattr(settings, "LOGIN_EXEMPT_URL_NAMES", [])
        )
        self.exempt_prefixes = tuple(
            getattr(settings, "LOGIN_EXEMPT_PREFIXES", [])
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated and not self._is_exempt(request):
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)

    def _is_exempt(self, request: HttpRequest) -> bool:
        path = request.path_info
        if path.startswith(self.exempt_prefixes):
            return True
        try:
            match = resolve(path)
        except Exception:
            return False
        # Match by namespaced URL name (e.g. "accounts:login").
        full_name = match.view_name
        return (
            full_name in self.exempt_names
            or match.url_name in self.exempt_names
        )


class ActiveUserMiddleware:
    """Immediately log out users who have been deactivated."""

    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and not user.is_active:
            # Capture the path before logout() flushes the session.
            next_path = request.get_full_path()
            logout(request)
            messages.error(
                request,
                "Your account has been disabled. Contact your administrator.",
            )
            return redirect_to_login(next_path)
        return self.get_response(request)
