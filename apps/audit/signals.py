from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from apps.audit.services import AuditService

User = get_user_model()


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Automatically logs audit logs when a user logs in successfully."""
    # Obtain user IP address if available
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    AuditService.log(
        user=user,
        action="Login",
        details="User logged in successfully via Web UI.",
        ip_address=ip,
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Automatically logs audit logs when a user logs out."""
    if user:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        AuditService.log(
            user=user,
            action="Logout",
            details="User logged out.",
            ip_address=ip,
        )
