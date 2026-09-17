"""User identity model.

Phase 1 establishes only the *shape* of the identity model, because Django's
``AUTH_USER_MODEL`` and ``USERNAME_FIELD`` must be fixed before the first
migration — changing them later is error-prone. Authentication flows, the Role
model, group wiring, profile, and avatar upload are added in Phase 2 as
additive migrations.

Design decisions:

* Email is the login identifier (``USERNAME_FIELD = "email"``); App Flow's
  login form authenticates by email.
* ``username`` is retained as an optional, unique display handle.
* The primary key is a UUID, consistent with the schema-wide convention.
* Soft deletion is enabled (users are a schema-approved soft-delete target).
"""

import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from apps.common.models import BaseModel, SoftDeleteModel
from apps.common.validators import ImageFileValidator


class Role(BaseModel):
    """A named role that maps 1:1 to a Django auth Group.

    The Group is the permission engine (it owns the permission set); this Role
    row provides a stable, human-friendly reference for assignment and display.
    ``UserService`` keeps a user's ``role`` FK and Group membership in sync so
    there is a single assignment path and no divergence between the two.
    """

    class Name(models.TextChoices):
        ADMINISTRATOR = "administrator", "Administrator"
        INVENTORY_MANAGER = "inventory_manager", "Inventory Manager"
        SALES_STAFF = "sales_staff", "Sales Staff"

    name = models.CharField(
        max_length=50,
        unique=True,
        choices=Name.choices,
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "roles"
        verbose_name = "role"
        verbose_name_plural = "roles"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.get_name_display()


class CustomUserManager(UserManager):
    """User manager keyed on email instead of username.

    Mirrors Django's ``UserManager`` but treats email as the required
    identifier so ``createsuperuser`` and programmatic creation behave
    consistently with email-based login.

    It also honors soft deletion: ``get_queryset`` excludes soft-deleted users
    so that a deleted account disappears from listings and — because this is
    the default manager Django's auth backend uses — can no longer
    authenticate. Use ``User.all_objects`` to reach every row, deleted or not.
    """

    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        # Fall back to the email as the username when none is supplied, so the
        # unique username column is always populated.
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, SoftDeleteModel):
    """Application user authenticated by email.

    Inherits Django's permission machinery (groups, user permissions,
    ``is_staff``/``is_superuser``) from ``AbstractUser``; role-to-group wiring
    is layered on in Phase 2.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    email = models.EmailField("email address", unique=True)
    phone = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(
        upload_to="users/",
        blank=True,
        null=True,
        validators=[ImageFileValidator()],
        help_text="Profile picture (JPEG, PNG, or WEBP, max 5 MB).",
    )
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Attribution: who created/last-changed this account. Set by UserService
    # (e.g. an admin creating a user). Self-referential, so ``+`` disables the
    # reverse accessor to avoid clashes.
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()  # type: ignore[assignment,misc]
    all_objects = UserManager()  # type: ignore[misc]

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    @property
    def role_name(self) -> str:
        """Return the assigned role's machine name, or an empty string."""
        return self.role.name if self.role is not None else ""

    @property
    def is_administrator(self) -> bool:
        """True if the user holds the Administrator role or is a superuser."""
        return self.is_superuser or self.role_name == Role.Name.ADMINISTRATOR

    @property
    def is_inventory_manager(self) -> bool:
        """True if the user holds the Inventory Manager role."""
        return self.role_name == Role.Name.INVENTORY_MANAGER

    @property
    def is_sales_staff(self) -> bool:
        """True if the user holds the Sales Staff role."""
        return self.role_name == Role.Name.SALES_STAFF
