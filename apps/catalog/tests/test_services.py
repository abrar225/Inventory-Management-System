import pytest

from apps.catalog.models import Category, Product, Supplier
from apps.catalog.services import (
    CategoryService,
    ProductService,
    SupplierService,
)

pytestmark = pytest.mark.django_db


class TestCategoryService:
    def test_create_category(self):
        category = CategoryService.create_category(
            name="Office Supplies",
            description="Paper, pens, etc."
        )
        assert category.name == "Office Supplies"
        assert category.description == "Paper, pens, etc."
        assert category.is_active is True

    def test_update_category(self):
        category = CategoryService.create_category(name="Office Supplies")
        updated = CategoryService.update_category(
            category,
            name="Office Supplies & Stationery",
            description="All desk items",
            is_active=False
        )
        assert updated.name == "Office Supplies & Stationery"
        assert updated.description == "All desk items"
        assert updated.is_active is False

    def test_delete_category(self):
        category = CategoryService.create_category(name="Office Supplies")
        CategoryService.delete_category(category)
        assert Category.objects.filter(pk=category.pk).count() == 0
        assert Category.all_objects.filter(pk=category.pk).count() == 1


class TestSupplierService:
    def test_create_supplier(self):
        supplier = SupplierService.create_supplier(
            company_name="Staples",
            contact_person="Alice",
            email="alice@staples.com",
            phone="1234567890",
            address="Commercial St"
        )
        assert supplier.company_name == "Staples"
        assert supplier.contact_person == "Alice"

    def test_update_supplier(self):
        supplier = SupplierService.create_supplier(
            company_name="Staples",
            contact_person="Alice",
            email="alice@staples.com",
            phone="1234567890"
        )
        updated = SupplierService.update_supplier(
            supplier,
            company_name="Staples Business Center",
            contact_person="Bob"
        )
        assert updated.company_name == "Staples Business Center"
        assert updated.contact_person == "Bob"

    def test_delete_supplier(self):
        supplier = SupplierService.create_supplier(
            company_name="Staples",
            contact_person="Alice",
            email="alice@staples.com",
            phone="1234567890"
        )
        SupplierService.delete_supplier(supplier)
        assert Supplier.objects.filter(pk=supplier.pk).count() == 0
        assert Supplier.all_objects.filter(pk=supplier.pk).count() == 1


class TestProductService:
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Paper")

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(
            company_name="Paper Co",
            contact_person="Joe",
            email="joe@paper.com",
            phone="555-5555"
        )

    def test_create_product(self, category, supplier):
        product = ProductService.create_product(
            sku="PAP-A4-100",
            name="A4 Paper Pack",
            category=category,
            supplier=supplier,
            purchase_price=200.00,
            selling_price=250.00,
            current_stock=100
        )
        assert product.sku == "PAP-A4-100"
        assert product.current_stock == 100

    def test_update_product(self, category, supplier):
        product = ProductService.create_product(
            sku="PAP-A4-100",
            name="A4 Paper Pack",
            category=category,
            supplier=supplier,
            purchase_price=200.00,
            selling_price=250.00
        )
        updated = ProductService.update_product(
            product,
            name="A4 Premium Paper Pack",
            selling_price=275.00
        )
        assert updated.name == "A4 Premium Paper Pack"
        assert updated.selling_price == 275.00

    def test_delete_product(self, category, supplier):
        product = ProductService.create_product(
            sku="PAP-A4-100",
            name="A4 Paper Pack",
            category=category,
            supplier=supplier,
            purchase_price=200.00,
            selling_price=250.00
        )
        ProductService.delete_product(product)
        assert Product.objects.filter(pk=product.pk).count() == 0
        assert Product.all_objects.filter(pk=product.pk).count() == 1
