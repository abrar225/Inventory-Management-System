"""App configuration for the common (shared utilities) app."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Shared base models, mixins, validators, and error views."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    verbose_name = "Common"
