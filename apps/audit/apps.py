"""App configuration for the audit app."""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Immutable audit log of critical actions."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Audit"

    def ready(self):
        import apps.audit.signals  # noqa
