"""App configuration for the inventory app."""

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Stock ledger, movements, and adjustments."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inventory"
    verbose_name = "Inventory"
