"""Service layer for user and role management.

All user lifecycle operations that touch roles, groups, or activation go
through ``UserService`` so there is a single, transactional assignment path.
Views must not manipulate ``user.role`` or ``user.groups`` directly — doing so
would risk the FK and Group membership diverging.
"""

import logging

from django.contrib.auth.models import Group
from django.db import transaction

from apps.accounts.models import Role, User

logger = logging.getLogger("ims")


class UserService:
    """Domain operations for users and their roles."""

    @staticmethod
    @transaction.atomic
    def create_user(
        *,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        role: Role | None = None,
        is_active: bool = True,
        created_by: "User | None" = None,
    ) -> "User":
        """Create a user and assign their role (and matching Group).

        Runs atomically so a user is never left half-created without their
        Group membership.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )
        if created_by is not None:
            user.created_by = created_by
            user.updated_by = created_by
            user.save(update_fields=["created_by", "updated_by"])
        if role is not None:
            UserService.assign_role(user, role, changed_by=created_by)
        logger.info("User created: %s", user.email)

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=created_by,
            action="Create User",
            model_name="User",
            object_id=str(user.id),
            object_repr=user.email,
            details=f"Created user account {user.email} with role {role.name if role else 'None'}.",
        )

        return user

    @staticmethod
    @transaction.atomic
    def assign_role(
        user: "User",
        role: Role,
        *,
        changed_by: "User | None" = None,
    ) -> "User":
        """Assign a role to a user and sync Group membership.

        Removes the user from any other role-backed Group and adds them to the
        one matching ``role``, so Group membership always reflects exactly one
        role. Non-role Groups (if any are ever added) are left untouched.
        """
        # Groups that correspond to roles, by role machine name.
        role_group_names = set(Role.Name.values)
        # Drop membership in any role-backed group the user currently has.
        user.groups.remove(
            *user.groups.filter(name__in=role_group_names)
        )
        group, _ = Group.objects.get_or_create(name=role.name)
        user.groups.add(group)

        user.role = role
        if changed_by is not None:
            user.updated_by = changed_by
        user.save(update_fields=["role", "updated_by"])
        logger.info("Role '%s' assigned to %s", role.name, user.email)

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=changed_by,
            action="Assign Role",
            model_name="User",
            object_id=str(user.id),
            object_repr=user.email,
            details=f"Assigned role {role.name} to user {user.email}.",
        )

        return user

    @staticmethod
    @transaction.atomic
    def deactivate_user(
        user: "User", *, changed_by: "User | None" = None
    ) -> "User":
        """Deactivate a user so they can no longer authenticate."""
        user.is_active = False
        if changed_by is not None:
            user.updated_by = changed_by
        user.save(update_fields=["is_active", "updated_by"])
        logger.info("User deactivated: %s", user.email)

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=changed_by,
            action="Deactivate User",
            model_name="User",
            object_id=str(user.id),
            object_repr=user.email,
            details=f"Deactivated user account {user.email}.",
        )

        return user

    @staticmethod
    @transaction.atomic
    def activate_user(
        user: "User", *, changed_by: "User | None" = None
    ) -> "User":
        """Reactivate a previously deactivated user."""
        user.is_active = True
        if changed_by is not None:
            user.updated_by = changed_by
        user.save(update_fields=["is_active", "updated_by"])
        logger.info("User activated: %s", user.email)

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=changed_by,
            action="Activate User",
            model_name="User",
            object_id=str(user.id),
            object_repr=user.email,
            details=f"Activated user account {user.email}.",
        )

        return user

    @staticmethod
    @transaction.atomic
    def set_password(
        user: "User", raw_password: str, *, changed_by: "User | None" = None
    ) -> "User":
        """Set a user's password (admin-initiated reset)."""
        user.set_password(raw_password)
        if changed_by is not None:
            user.updated_by = changed_by
        user.save(update_fields=["password", "updated_by"])
        logger.info("Password reset for %s", user.email)

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=changed_by,
            action="Reset Password",
            model_name="User",
            object_id=str(user.id),
            object_repr=user.email,
            details=f"Reset password credentials for user account {user.email}.",
        )

        return user
