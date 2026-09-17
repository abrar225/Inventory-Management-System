"""Shared abstract models used across every domain app.

The schema mandates UUID primary keys and timestamps on every table. Two
abstract bases are provided:

* ``BaseModel`` — mutable entities (products, suppliers, purchases, ...).
  Carries ``created_at``/``updated_at`` plus ``created_by``/``updated_by``.
* ``ImmutableBaseModel`` — append-only records (stock ledger, audit log).
  Carries ``created_at``/``created_by`` only; there is no ``updated_*`` because
  nothing may ever update these rows.

Soft deletion is provided separately via ``SoftDeleteModel`` and is applied
only where the Backend Schema explicitly allows it (products, suppliers,
categories, users).
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Manager


class UUIDPrimaryKeyModel(models.Model):
    """Abstract model providing a UUID version-4 primary key."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract model adding creation and modification timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDPrimaryKeyModel, TimeStampedModel):
    """Standard base for mutable domain entities.

    Provides a UUID primary key, timestamps, and nullable user-attribution
    fields. ``created_by``/``updated_by`` are set by the service layer rather
    than by signals, keeping attribution explicit.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ImmutableBaseModel(UUIDPrimaryKeyModel):
    """Base for append-only records (stock movements, audit logs).

    Immutable rows carry only creation metadata — there is deliberately no
    ``updated_at``/``updated_by``, because these records are never modified
    after insertion.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet exposing soft-delete-aware helpers."""

    def alive(self) -> "SoftDeleteQuerySet":
        """Return only rows that have not been soft-deleted."""
        return self.filter(is_deleted=False)

    def dead(self) -> "SoftDeleteQuerySet":
        """Return only rows that have been soft-deleted."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Default manager that hides soft-deleted rows.

    ``all_objects`` (attached on the model) exposes every row including
    deleted ones for admin and reconciliation use.
    """

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            is_deleted=False
        )

    def alive(self) -> SoftDeleteQuerySet:
        """Return only rows that have not been soft-deleted."""
        return self.get_queryset().alive()

    def dead(self) -> SoftDeleteQuerySet:
        """Return only rows that have been soft-deleted."""
        return self.get_queryset().dead()


class SoftDeleteModel(models.Model):
    """Adds reversible soft deletion.

    Applied only to models the schema permits (products, suppliers,
    categories, users). Historical/immutable records must never inherit this.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    all_objects = Manager()
    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: flag the row instead of removing it."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently remove the row (reserved for maintenance tasks)."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Reverse a soft delete."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])
