import datetime
import uuid
from decimal import Decimal

from django.db import transaction

from apps.accounts.models import User
from apps.inventory.models import StockMovement
from apps.inventory.services import InventoryService
from apps.sales.models import Sale, SaleItem


def generate_invoice_number() -> str:
    """Generates a unique Invoice number."""
    today = datetime.date.today().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"INV-{today}-{unique_suffix}"


class SalesService:
    """Business logic layer for Sales Invoices."""

    @staticmethod
    @transaction.atomic
    def create_sale(
        customer_name: str,
        sale_date,
        items_data,
        user: User,
        discount=0.0,
        tax=0.0,
    ) -> Sale:
        """Atomically processes a Sale, checks stock levels, and records ledger entries."""
        invoice_number = generate_invoice_number()

        # Instantiate Sale header
        sale = Sale(
            invoice_number=invoice_number,
            customer_name=customer_name,
            sale_date=sale_date,
            discount=Decimal(str(discount)),
            tax=Decimal(str(tax)),
            status=Sale.Status.COMPLETED,
            created_by=user,
            updated_by=user,
        )
        sale.save()

        subtotal = Decimal("0.00")
        for item in items_data:
            product = item["product"]
            qty = int(item["quantity"])
            price = Decimal(str(item["unit_price"]))
            line_total = qty * price
            subtotal += line_total

            # Verify stock level availability and deduct stock.
            # InventoryService.record_movement raises InsufficientStockError if quantity falls below 0.
            InventoryService.record_movement(
                product=product,
                quantity=-qty,
                movement_type=StockMovement.MovementType.SALE,
                reference_type=StockMovement.ReferenceType.SALE,
                reference_id=str(sale.id),
                reason=f"Sold on Invoice {sale.invoice_number}",
                created_by=user,
            )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=qty,
                unit_price=price,
                line_total=line_total,
            )

        sale.subtotal = subtotal
        sale.grand_total = (
            subtotal + Decimal(str(tax)) - Decimal(str(discount))
        )
        sale.save(update_fields=["subtotal", "grand_total"])

        # Log audit trail action
        from apps.audit.services import AuditService

        AuditService.log(
            user=user,
            action="Complete Sale",
            model_name="Sale",
            object_id=str(sale.id),
            object_repr=sale.invoice_number,
            details=f"Completed sale invoice {sale.invoice_number} to customer {sale.customer_name} for ₹{sale.grand_total}.",
        )

        return sale
