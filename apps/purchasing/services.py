import datetime
import uuid
from decimal import Decimal

from django.db import transaction

from apps.accounts.models import User
from apps.inventory.models import StockMovement
from apps.inventory.services import InventoryService
from apps.purchasing.models import Purchase, PurchaseItem


def generate_purchase_number() -> str:
    """Generates a unique Purchase Order transaction number."""
    today = datetime.date.today().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"PO-{today}-{unique_suffix}"


class PurchasingService:
    """Business logic layer for Purchase Orders."""

    @staticmethod
    @transaction.atomic
    def create_purchase(
        supplier,
        purchase_date,
        items_data,
        user: User,
        discount=0.0,
        tax=0.0,
        notes="",
    ) -> Purchase:
        """Creates a Purchase Order and inserts related items atomically."""
        purchase_number = generate_purchase_number()

        purchase = Purchase(
            purchase_number=purchase_number,
            supplier=supplier,
            purchase_date=purchase_date,
            discount=Decimal(str(discount)),
            tax=Decimal(str(tax)),
            notes=notes,
            status=Purchase.Status.ORDERED,
            created_by=user,
            updated_by=user,
        )
        purchase.save()

        subtotal = Decimal("0.00")
        for item in items_data:
            qty = int(item["quantity"])
            price = Decimal(str(item["unit_price"]))
            line_total = qty * price
            subtotal += line_total

            PurchaseItem.objects.create(
                purchase=purchase,
                product=item["product"],
                quantity=qty,
                unit_price=price,
                line_total=line_total,
            )

        purchase.subtotal = subtotal
        purchase.grand_total = (
            subtotal + Decimal(str(tax)) - Decimal(str(discount))
        )
        purchase.save(update_fields=["subtotal", "grand_total"])
        return purchase

    @staticmethod
    @transaction.atomic
    def receive_purchase(purchase: Purchase, user: User) -> Purchase:
        """Confirms receipt of ordered inventory.

        Increases product stock and registers ledger events.
        """
        if purchase.status == Purchase.Status.RECEIVED:
            raise ValueError("Purchase Order is already received.")
        if purchase.status == Purchase.Status.CANCELLED:
            raise ValueError("Cannot receive a cancelled Purchase Order.")

        # Increase stock levels for all products on the purchase order
        for item in purchase.items.all():
            InventoryService.record_movement(
                product=item.product,
                quantity=item.quantity,
                movement_type=StockMovement.MovementType.PURCHASE,
                reference_type=StockMovement.ReferenceType.PURCHASE,
                reference_id=str(purchase.id),
                reason=f"Received Purchase Order {purchase.purchase_number}",
                created_by=user,
            )

        purchase.status = Purchase.Status.RECEIVED
        purchase.updated_by = user
        purchase.save(update_fields=["status", "updated_by", "updated_at"])

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=user,
            action="Receive Purchase Order",
            model_name="Purchase",
            object_id=str(purchase.id),
            object_repr=purchase.purchase_number,
            details=f"Received PO {purchase.purchase_number} from supplier {purchase.supplier.company_name}.",
        )

        return purchase
