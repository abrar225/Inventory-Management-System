import uuid

from django.db import models

from apps.common.models import BaseModel


class Purchase(BaseModel):
    """Purchase Order model representing inward supply acquisition transactions."""

    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        ORDERED = "Ordered", "Ordered"
        RECEIVED = "Received", "Received"
        CANCELLED = "Cancelled", "Cancelled"

    purchase_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        "catalog.Supplier",
        on_delete=models.PROTECT,
        related_name="purchases",
    )
    purchase_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchases"
        ordering = ["-purchase_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.purchase_number} - {self.supplier.company_name} ({self.status})"


class PurchaseItem(models.Model):
    """Individual line items for a Purchase Order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "purchase_items"

    def __str__(self) -> str:
        return f"{self.product.name} (Qty: {self.quantity})"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
