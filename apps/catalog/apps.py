"""App configuration for the catalog app."""

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Product catalog: categories, suppliers, and products."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Catalog"
