from django.db import models

from apps.common.models import BaseModel


class StockMovement(BaseModel):
    """Immutable ledger record of a change in product stock.

    Every stock modification (purchases, sales, adjustments) must write
    a row here. Records here are never updated or deleted.
    """

    class MovementType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sale"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    class ReferenceType(models.TextChoices):
        PURCHASE = "Purchase", "Purchase"
        SALE = "Sale", "Sale"
        ADJUSTMENT = "Adjustment", "Adjustment"

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    reference_type = models.CharField(
        max_length=20,
        choices=ReferenceType.choices,
    )
    reference_id = models.UUIDField(null=True, blank=True)
    quantity = models.IntegerField(
        help_text="Stock quantity changed. Negative for outward, positive for inward."
    )
    balance_after = models.IntegerField(
        help_text="The total current stock of the product after this movement."
    )
    reason = models.TextField(blank=True)

    class Meta:
        db_table = "stock_movements"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.product.name} ({self.movement_type}): {self.quantity:+} (Bal: {self.balance_after})"


class StockAdjustment(BaseModel):
    """Record of manual inventory changes/reconciliations.

    This includes corrections, damage reports, returns, etc.
    """

    class AdjustmentType(models.TextChoices):
        INCREASE = "Increase", "Increase"
        DECREASE = "Decrease", "Decrease"
        CORRECTION = "Correction", "Correction"
        DAMAGE = "Damage", "Damage"
        RETURN = "Return", "Return"
        LOST = "Lost", "Lost"

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="stock_adjustments",
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=AdjustmentType.choices,
    )
    quantity = models.PositiveIntegerField(
        help_text="The magnitude of the stock adjustment (always positive)."
    )
    reason = models.TextField()
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_adjustments",
    )

    class Meta:
        db_table = "stock_adjustments"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.adjustment_type} of {self.quantity}"
