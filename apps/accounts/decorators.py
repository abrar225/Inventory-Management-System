"""Authorization decorators and mixins for views.

Permission enforcement is mandatory on every protected view. These helpers
build on Django's auth framework:

* ``role_required`` — restrict a function view to specific roles.
* ``RoleRequiredMixin`` — the class-based-view equivalent.

Permission-level checks (e.g. ``permission_required("catalog.add_product")``)
use Django's built-in decorators/mixins directly, since Groups carry the
permissions. These role helpers are for coarse, role-based gating where a
permission codename would be less readable.

Unauthorized authenticated users receive a 403 (rendered by the common error
handler); unauthenticated users are redirected to login by Django's
``login_required`` machinery.
"""

from collections.abc import Callable, Iterable
from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse


def _has_role(user, roles: Iterable[str]) -> bool:
    """Return True if the user holds one of ``roles`` (superuser passes)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role_name in set(roles)


def role_required(
    *roles: str,
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Restrict a function-based view to the given role machine names.

    Example::

        @role_required(Role.Name.ADMINISTRATOR)
        def user_list(request): ...

    Raises ``PermissionDenied`` (403) for authenticated users lacking the
    role. Unauthenticated users are sent to the login page.
    """

    def decorator(
        view_func: Callable[..., HttpResponse],
    ) -> Callable[..., HttpResponse]:
        @wraps(view_func)
        def _wrapped(
            request: HttpRequest, *args, **kwargs
        ) -> HttpResponse:
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path())
            if not _has_role(request.user, roles):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin(AccessMixin):
    """Class-based-view mixin restricting access to ``allowed_roles``.

    Set ``allowed_roles`` to an iterable of role machine names. Superusers
    always pass. Unauthenticated users are redirected to login; authenticated
    users without a matching role get a 403.
    """

    allowed_roles: Iterable[str] = ()

    def dispatch(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not _has_role(request.user, self.allowed_roles):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]
