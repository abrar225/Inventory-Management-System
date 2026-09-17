"""Reconcile Roles and permission Groups from the permission matrix.

Idempotent and safe to re-run at any phase: it seeds the three Role rows,
creates the matching auth Groups, and reconciles each Group's permission set
to exactly match ``apps.accounts.permissions.ROLE_PERMISSIONS``. The
Administrator group receives every permission.

Because business models arrive in later phases, permissions referenced in the
matrix that do not exist yet are skipped with a warning rather than failing —
re-run this command after each phase's migrations to grant newly created
permissions.

Usage::

    python manage.py sync_roles
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role
from apps.accounts.permissions import ROLE_DESCRIPTIONS, ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Seed roles and sync auth groups with the permission matrix."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        self._seed_roles()
        self._sync_administrator()
        self._sync_matrix_roles()
        self.stdout.write(self.style.SUCCESS("Roles and groups synced."))

    def _seed_roles(self) -> None:
        """Create/update the three Role rows and their backing Groups."""
        for name, _label in Role.Name.choices:
            role, created = Role.objects.get_or_create(name=name)
            description = ROLE_DESCRIPTIONS.get(name, "")
            if role.description != description:
                role.description = description
                role.save(update_fields=["description"])
            Group.objects.get_or_create(name=name)
            verb = "Created" if created else "Verified"
            self.stdout.write(f"  {verb} role/group: {name}")

    def _sync_administrator(self) -> None:
        """Grant the Administrator group every permission."""
        group = Group.objects.get(name=Role.Name.ADMINISTRATOR)
        all_perms = Permission.objects.all()
        group.permissions.set(all_perms)
        self.stdout.write(
            f"  Administrator: {all_perms.count()} permissions granted."
        )

    def _sync_matrix_roles(self) -> None:
        """Reconcile each matrix-defined group to its permission list."""
        for role_name, perm_codes in ROLE_PERMISSIONS.items():
            group = Group.objects.get(name=role_name)
            resolved, missing = self._resolve_permissions(perm_codes)
            group.permissions.set(resolved)
            self.stdout.write(
                f"  {role_name}: {len(resolved)} permissions granted."
            )
            for code in missing:
                self.stdout.write(
                    self.style.WARNING(
                        f"    skipped unknown permission '{code}' "
                        "(model not yet migrated?)"
                    )
                )

    def _resolve_permissions(
        self, codes: list[str]
    ) -> tuple[list[Permission], list[str]]:
        """Resolve ``app_label.codename`` strings to Permission objects.

        Returns the resolved permissions and the list of codes that could not
        be found (their models likely arrive in a later phase).
        """
        resolved: list[Permission] = []
        missing: list[str] = []
        for code in codes:
            try:
                app_label, codename = code.split(".", 1)
            except ValueError:
                missing.append(code)
                continue
            perm = Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
            if perm is None:
                missing.append(code)
            else:
                resolved.append(perm)
        return resolved, missing
