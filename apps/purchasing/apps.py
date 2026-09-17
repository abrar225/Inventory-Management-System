"""App configuration for the purchasing app."""

from django.apps import AppConfig


class PurchasingConfig(AppConfig):
    """Purchases and purchase items (increase inventory)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.purchasing"
    verbose_name = "Purchasing"
