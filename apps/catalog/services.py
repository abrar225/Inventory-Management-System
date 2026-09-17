import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Category, Product, Supplier

logger = logging.getLogger("ims")
User = get_user_model()


class CategoryService:
    """Service layer for Category domain operations."""

    @staticmethod
    @transaction.atomic
    def create_category(
        *,
        name: str,
        description: str = "",
        is_active: bool = True,
        created_by: Any | None = None,
    ) -> Category:
        """Create a new category."""
        category = Category.objects.create(
            name=name,
            description=description,
            is_active=is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        logger.info("Category created: %s", category.name)
        return category

    @staticmethod
    @transaction.atomic
    def update_category(
        category: Category,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        updated_by: Any | None = None,
    ) -> Category:
        """Update an existing category."""
        update_fields = []
        if name is not None:
            category.name = name
            category.slug = slugify(name)
            update_fields.extend(["name", "slug"])
        if description is not None:
            category.description = description
            update_fields.append("description")
        if is_active is not None:
            category.is_active = is_active
            update_fields.append("is_active")
        if updated_by is not None:
            category.updated_by = updated_by
            update_fields.append("updated_by")

        if update_fields:
            category.save(update_fields=update_fields)
            logger.info("Category updated: %s", category.name)
        return category

    @staticmethod
    @transaction.atomic
    def delete_category(category: Category) -> None:
        """Soft delete a category."""
        category.delete()
        logger.info("Category soft-deleted: %s", category.name)


class SupplierService:
    """Service layer for Supplier domain operations."""

    @staticmethod
    @transaction.atomic
    def create_supplier(
        *,
        company_name: str,
        contact_person: str,
        email: str,
        phone: str,
        gst_number: str = "",
        address: str = "",
        city: str = "",
        state: str = "",
        postal_code: str = "",
        country: str = "India",
        notes: str = "",
        is_active: bool = True,
        created_by: Any | None = None,
    ) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            gst_number=gst_number,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            notes=notes,
            is_active=is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        logger.info("Supplier created: %s", supplier.company_name)
        return supplier

    @staticmethod
    @transaction.atomic
    def update_supplier(
        supplier: Supplier,
        *,
        company_name: str | None = None,
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        gst_number: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        country: str | None = None,
        notes: str | None = None,
        is_active: bool | None = None,
        updated_by: Any | None = None,
    ) -> Supplier:
        """Update an existing supplier."""
        update_fields = []
        if company_name is not None:
            supplier.company_name = company_name
            update_fields.append("company_name")
        if contact_person is not None:
            supplier.contact_person = contact_person
            update_fields.append("contact_person")
        if email is not None:
            supplier.email = email
            update_fields.append("email")
        if phone is not None:
            supplier.phone = phone
            update_fields.append("phone")
        if gst_number is not None:
            supplier.gst_number = gst_number
            update_fields.append("gst_number")
        if address is not None:
            supplier.address = address
            update_fields.append("address")
        if city is not None:
            supplier.city = city
            update_fields.append("city")
        if state is not None:
            supplier.state = state
            update_fields.append("state")
        if postal_code is not None:
            supplier.postal_code = postal_code
            update_fields.append("postal_code")
        if country is not None:
            supplier.country = country
            update_fields.append("country")
        if notes is not None:
            supplier.notes = notes
            update_fields.append("notes")
        if is_active is not None:
            supplier.is_active = is_active
            update_fields.append("is_active")
        if updated_by is not None:
            supplier.updated_by = updated_by
            update_fields.append("updated_by")

        if update_fields:
            supplier.save(update_fields=update_fields)
            logger.info("Supplier updated: %s", supplier.company_name)
        return supplier

    @staticmethod
    @transaction.atomic
    def delete_supplier(supplier: Supplier) -> None:
        """Soft delete a supplier."""
        supplier.delete()
        logger.info("Supplier soft-deleted: %s", supplier.company_name)


class ProductService:
    """Service layer for Product domain operations."""

    @staticmethod
    @transaction.atomic
    def create_product(
        *,
        sku: str,
        name: str,
        category: Category,
        supplier: Supplier,
        purchase_price: float,
        selling_price: float,
        barcode: str | None = None,
        current_stock: int = 0,
        minimum_stock: int = 5,
        unit: str = "PCS",
        description: str = "",
        image: Any | None = None,
        is_active: bool = True,
        created_by: Any | None = None,
    ) -> Product:
        """Create a new product."""
        product = Product.objects.create(
            sku=sku,
            barcode=barcode,
            name=name,
            category=category,
            supplier=supplier,
            purchase_price=purchase_price,
            selling_price=selling_price,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            unit=unit,
            description=description,
            image=image,
            is_active=is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        logger.info("Product created: %s (%s)", product.name, product.sku)
        return product

    @staticmethod
    @transaction.atomic
    def update_product(
        product: Product,
        *,
        sku: str | None = None,
        barcode: str | None = None,
        name: str | None = None,
        category: Category | None = None,
        supplier: Supplier | None = None,
        purchase_price: float | None = None,
        selling_price: float | None = None,
        current_stock: int | None = None,
        minimum_stock: int | None = None,
        unit: str | None = None,
        description: str | None = None,
        image: Any | None = None,
        is_active: bool | None = None,
        updated_by: Any | None = None,
    ) -> Product:
        """Update an existing product."""
        update_fields = []
        if sku is not None:
            product.sku = sku
            update_fields.append("sku")
        if barcode is not None:
            product.barcode = barcode
            update_fields.append("barcode")
        if name is not None:
            product.name = name
            product.slug = slugify(name)
            update_fields.extend(["name", "slug"])
        if category is not None:
            product.category = category
            update_fields.append("category")
        if supplier is not None:
            product.supplier = supplier
            update_fields.append("supplier")
        if purchase_price is not None:
            product.purchase_price = purchase_price
            update_fields.append("purchase_price")
        if selling_price is not None:
            product.selling_price = selling_price
            update_fields.append("selling_price")
        if current_stock is not None:
            product.current_stock = current_stock
            update_fields.append("current_stock")
        if minimum_stock is not None:
            product.minimum_stock = minimum_stock
            update_fields.append("minimum_stock")
        if unit is not None:
            product.unit = unit
            update_fields.append("unit")
        if description is not None:
            product.description = description
            update_fields.append("description")
        if image is not None:
            product.image = image
            update_fields.append("image")
        if is_active is not None:
            product.is_active = is_active
            update_fields.append("is_active")
        if updated_by is not None:
            product.updated_by = updated_by
            update_fields.append("updated_by")

        if update_fields:
            product.save(update_fields=update_fields)
            logger.info("Product updated: %s (%s)", product.name, product.sku)
        return product

    @staticmethod
    @transaction.atomic
    def delete_product(product: Product) -> None:
        """Soft delete a product."""
        product.delete()
        logger.info("Product soft-deleted: %s (%s)", product.name, product.sku)
