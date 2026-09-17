"""Admin registration for the User model.

A minimal registration in Phase 1 so users can be inspected and a superuser
managed via ``/admin``. Role and group administration is expanded in Phase 2.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Read-oriented admin for the fixed set of roles."""

    list_display = ["name", "description"]
    search_fields = ["name", "description"]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Email-first user admin."""

    ordering = ["email"]
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_active",
    ]
    list_filter = ["role", "is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "username", "first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
