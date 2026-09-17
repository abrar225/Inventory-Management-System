"""App configuration for the sales app."""

from django.apps import AppConfig


class SalesConfig(AppConfig):
    """Sales and sale items (decrease inventory)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sales"
    verbose_name = "Sales"
