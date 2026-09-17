"""Data migration: seed the three roles and their backing auth groups.

Creates the Role rows and matching Groups so a fresh database is bootstrapped
by ``migrate`` alone. Permission assignment is deliberately left to the
``sync_roles`` management command, because most business-model permissions do
not exist until their apps are migrated in later phases. Run ``sync_roles``
after migrating to grant permissions.

The operation is reversible and idempotent.
"""

from django.db import migrations

ROLES = [
    ("administrator", "Full system access, including users and audit logs."),
    (
        "inventory_manager",
        "Manages catalog, purchases, sales, and inventory. No user or audit "
        "administration.",
    ),
    (
        "sales_staff",
        "Records sales and views products and inventory. Read-only reporting.",
    ),
]


def seed_roles_and_groups(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Group = apps.get_model("auth", "Group")
    for name, description in ROLES:
        Role.objects.update_or_create(
            name=name, defaults={"description": description}
        )
        Group.objects.get_or_create(name=name)


def remove_roles_and_groups(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Group = apps.get_model("auth", "Group")
    names = [name for name, _ in ROLES]
    Role.objects.filter(name__in=names).delete()
    Group.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_avatar_role_user_role"),
    ]

    operations = [
        migrations.RunPython(
            seed_roles_and_groups, remove_roles_and_groups
        ),
    ]
