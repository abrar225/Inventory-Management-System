"""App configuration for the reporting app."""

from django.apps import AppConfig


class ReportingConfig(AppConfig):
    """Read-model reports and exports."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reporting"
    verbose_name = "Reporting"
