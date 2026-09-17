from django.db import transaction

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.inventory.models import StockAdjustment, StockMovement


class InsufficientStockError(Exception):
    """Raised when a stock movement would cause stock to drop below zero."""

    pass


class InventoryService:
    """Business logic for inventory operations and ledger management."""

    @staticmethod
    @transaction.atomic
    def adjust_stock(
        product: Product,
        quantity: int,
        adjustment_type: str,
        reason: str,
        created_by: User,
    ) -> StockAdjustment:
        """Atomically adjusts product stock and writes ledger movements."""
        # Calculate the net change based on adjustment type
        if adjustment_type in [
            StockAdjustment.AdjustmentType.INCREASE,
            StockAdjustment.AdjustmentType.RETURN,
        ]:
            net_change = quantity
        elif adjustment_type in [
            StockAdjustment.AdjustmentType.DECREASE,
            StockAdjustment.AdjustmentType.DAMAGE,
            StockAdjustment.AdjustmentType.LOST,
        ]:
            net_change = -quantity
        elif adjustment_type == StockAdjustment.AdjustmentType.CORRECTION:
            # Correction quantity can be signed (positive for increase, negative for decrease)
            net_change = quantity
        else:
            raise ValueError(f"Invalid adjustment type: {adjustment_type}")

        # Enforce negative stock prevention
        new_stock = product.current_stock + net_change
        if new_stock < 0:
            raise InsufficientStockError(
                f"Insufficient stock for {product.name}. Current: {product.current_stock}, "
                f"Requested adjustment: {net_change:+}."
            )

        # Update product current stock level
        product.current_stock = new_stock
        product.save(update_fields=["current_stock", "updated_at"])

        # Create StockAdjustment record (always stores absolute magnitude of change)
        adjustment = StockAdjustment.objects.create(
            product=product,
            adjustment_type=adjustment_type,
            quantity=abs(quantity),
            reason=reason,
            created_by=created_by,
        )

        # Create StockMovement ledger entry
        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            reference_type=StockMovement.ReferenceType.ADJUSTMENT,
            reference_id=adjustment.id,
            quantity=net_change,
            balance_after=new_stock,
            reason=reason,
            created_by=created_by,
        )

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=created_by,
            action="Stock Adjustment",
            model_name="StockAdjustment",
            object_id=str(adjustment.id),
            object_repr=f"{product.name} (Change: {net_change:+})",
            details=f"Adjustment type: {adjustment_type}. Reason: {reason}",
        )

        return adjustment

    @staticmethod
    @transaction.atomic
    def reconcile_stock(
        product: Product,
        expected_quantity: int,
        reason: str,
        created_by: User,
    ) -> StockAdjustment:
        """Reconciles physical inventory count with database records."""
        if expected_quantity < 0:
            raise ValueError("Expected quantity cannot be negative.")

        diff = expected_quantity - product.current_stock
        if diff == 0:
            # Log as a correction with 0 quantity changed
            return StockAdjustment.objects.create(
                product=product,
                adjustment_type=StockAdjustment.AdjustmentType.CORRECTION,
                quantity=0,
                reason=reason,
                created_by=created_by,
            )

        return InventoryService.adjust_stock(
            product=product,
            quantity=diff,
            adjustment_type=StockAdjustment.AdjustmentType.CORRECTION,
            reason=reason,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def record_movement(
        product: Product,
        quantity: int,
        movement_type: str,
        reference_type: str,
        reference_id: str,
        reason: str,
        created_by: User,
    ) -> StockMovement:
        """Records an external stock movement (e.g. from purchase or sale)."""
        new_stock = product.current_stock + quantity
        if new_stock < 0:
            raise InsufficientStockError(
                f"Insufficient stock for {product.name}. Current: {product.current_stock}, "
                f"Requested change: {quantity:+}."
            )

        # Update product stock level
        product.current_stock = new_stock
        product.save(update_fields=["current_stock", "updated_at"])

        # Create StockMovement ledger entry
        return StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            reference_type=reference_type,
            reference_id=reference_id,
            quantity=quantity,
            balance_after=new_stock,
            reason=reason,
            created_by=created_by,
        )
