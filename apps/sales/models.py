import uuid

from django.db import models

from apps.common.models import BaseModel


class Sale(BaseModel):
    """Sale Invoice model representing outward supply sales transactions."""

    class Status(models.TextChoices):
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    invoice_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=150)
    sale_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
    )

    class Meta:
        db_table = "sales"
        ordering = ["-sale_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.invoice_number} - {self.customer_name} ({self.status})"


class SaleItem(models.Model):
    """Individual line items for a Sale Invoice."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="sale_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "sale_items"

    def __str__(self) -> str:
        return f"{self.product.name} (Qty: {self.quantity})"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
