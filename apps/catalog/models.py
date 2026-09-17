from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel, SoftDeleteModel
from apps.common.validators import ImageFileValidator


class Category(BaseModel, SoftDeleteModel):
    """Product categories.

    Each product belongs to exactly one category.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Supplier(BaseModel, SoftDeleteModel):
    """Suppliers who provide products."""

    company_name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    gst_number = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "suppliers"
        verbose_name = "supplier"
        verbose_name_plural = "suppliers"
        ordering = ["company_name"]

    def __str__(self) -> str:
        return self.company_name


class Product(BaseModel, SoftDeleteModel):
    """Products catalogued in the system."""

    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="products",
    )
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, default="PCS")
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True,
        validators=[ImageFileValidator()],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"
        verbose_name = "product"
        verbose_name_plural = "products"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self) -> bool:
        """Return True if stock is less than or equal to minimum stock."""
        return self.current_stock <= self.minimum_stock

    @property
    def is_out_of_stock(self) -> bool:
        """Return True if stock is zero or negative."""
        return self.current_stock <= 0
