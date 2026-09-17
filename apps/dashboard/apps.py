"""App configuration for the dashboard app."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Landing dashboard: KPIs, charts, and recent activity."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    verbose_name = "Dashboard"
