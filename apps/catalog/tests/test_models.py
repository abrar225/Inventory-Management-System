import pytest
from django.db import IntegrityError

from apps.catalog.models import Category, Product, Supplier

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_category_creation_and_slug(self):
        category = Category.objects.create(name="Electronics", description="Gadgets")
        assert category.slug == "electronics"
        assert str(category) == "Electronics"

    def test_category_unique_name(self):
        Category.objects.create(name="Electronics")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Electronics")


class TestSupplierModel:
    def test_supplier_creation(self):
        supplier = Supplier.objects.create(
            company_name="ACME Corp",
            contact_person="John Doe",
            email="john@acme.com",
            phone="1234567890",
            address="123 Main St",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
        )
        assert str(supplier) == "ACME Corp"
        assert supplier.country == "India"

    def test_supplier_unique_company_name(self):
        Supplier.objects.create(
            company_name="ACME Corp",
            contact_person="John Doe",
            email="john@acme.com",
            phone="1234567890",
            address="123 Main St",
        )
        with pytest.raises(IntegrityError):
            Supplier.objects.create(
                company_name="ACME Corp",
                contact_person="Jane Doe",
                email="jane@acme.com",
                phone="0987654321",
                address="456 Main St",
            )


class TestProductModel:
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Laptops")

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(
            company_name="Dell India",
            contact_person="Raj",
            email="raj@dell.com",
            phone="9876543210",
            address="Dell Tech Park",
        )

    def test_product_creation_and_slug(self, category, supplier):
        product = Product.objects.create(
            sku="DELL-XPS-13",
            name="Dell XPS 13",
            category=category,
            supplier=supplier,
            purchase_price=80000.00,
            selling_price=95000.00,
            current_stock=10,
        )
        assert product.slug == "dell-xps-13"
        assert str(product) == "Dell XPS 13 (DELL-XPS-13)"
        assert not product.is_low_stock
        assert not product.is_out_of_stock

    def test_product_stock_indicators(self, category, supplier):
        product = Product.objects.create(
            sku="DELL-XPS-13",
            name="Dell XPS 13",
            category=category,
            supplier=supplier,
            purchase_price=80000.00,
            selling_price=95000.00,
            current_stock=2,
            minimum_stock=5,
        )
        assert product.is_low_stock
        assert not product.is_out_of_stock

        product.current_stock = 0
        assert product.is_low_stock
        assert product.is_out_of_stock

    def test_product_unique_sku(self, category, supplier):
        Product.objects.create(
            sku="SKU-DUP",
            name="Product 1",
            category=category,
            supplier=supplier,
            purchase_price=10.00,
            selling_price=15.00,
        )
        with pytest.raises(IntegrityError):
            Product.objects.create(
                sku="SKU-DUP",
                name="Product 2",
                category=category,
                supplier=supplier,
                purchase_price=12.00,
                selling_price=18.00,
            )
