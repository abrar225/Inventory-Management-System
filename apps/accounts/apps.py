"""App configuration for the accounts (identity & auth) app."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Users, roles, permissions, and authentication flows."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Accounts"
