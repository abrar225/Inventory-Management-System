import pytest
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    # Create and login an admin/superuser to bypass permission checks easily for basic CRUD tests
    admin_user = UserFactory(is_superuser=True, is_staff=True)
    client.login(username=admin_user.email, password="password123!")
    return client


class TestCategoryViews:
    def test_category_list_view(self, admin_client):
        Category.objects.create(name="Hardware")
        Category.objects.create(name="Software")
        resp = admin_client.get(reverse("catalog:category_list"))
        assert resp.status_code == 200
        assert b"Hardware" in resp.content
        assert b"Software" in resp.content

    def test_category_create_view(self, admin_client):
        resp = admin_client.post(
            reverse("catalog:category_add"),
            {"name": "Books", "description": "Stationery items", "is_active": True}
        )
        assert resp.status_code == 302
        assert Category.objects.filter(name="Books").exists()

    def test_category_update_view(self, admin_client):
        cat = Category.objects.create(name="Books")
        resp = admin_client.post(
            reverse("catalog:category_edit", kwargs={"pk": cat.pk}),
            {"name": "Novels", "description": "Fiction books", "is_active": True}
        )
        assert resp.status_code == 302
        cat.refresh_from_db()
        assert cat.name == "Novels"

    def test_category_delete_view(self, admin_client):
        cat = Category.objects.create(name="Books")
        resp = admin_client.post(
            reverse("catalog:category_delete", kwargs={"pk": cat.pk})
        )
        assert resp.status_code == 302
        assert Category.objects.filter(pk=cat.pk).count() == 0
        assert Category.all_objects.filter(pk=cat.pk).count() == 1


class TestSupplierViews:
    def test_supplier_list_view(self, admin_client):
        Supplier.objects.create(company_name="Logitech", contact_person="Tim")
        resp = admin_client.get(reverse("catalog:supplier_list"))
        assert resp.status_code == 200
        assert b"Logitech" in resp.content

    def test_supplier_create_view(self, admin_client):
        resp = admin_client.post(
            reverse("catalog:supplier_add"),
            {
                "company_name": "Intel",
                "contact_person": "Gordon",
                "email": "gordon@intel.com",
                "phone": "9998887776",
                "address": "Silicon Valley",
                "city": "San Jose",
                "state": "California",
                "postal_code": "95101",
                "country": "USA",
                "is_active": True,
            }
        )
        assert resp.status_code == 302
        assert Supplier.objects.filter(company_name="Intel").exists()

    def test_supplier_update_view(self, admin_client):
        sup = Supplier.objects.create(company_name="Intel")
        resp = admin_client.post(
            reverse("catalog:supplier_edit", kwargs={"pk": sup.pk}),
            {
                "company_name": "Intel Corp",
                "contact_person": "Moore",
                "email": "moore@intel.com",
                "phone": "1112223334",
                "address": "San Jose Campus",
                "city": "San Jose",
                "state": "California",
                "postal_code": "95101",
                "country": "USA",
                "is_active": True,
            }
        )
        assert resp.status_code == 302
        sup.refresh_from_db()
        assert sup.company_name == "Intel Corp"

    def test_supplier_delete_view(self, admin_client):
        sup = Supplier.objects.create(company_name="Intel")
        resp = admin_client.post(
            reverse("catalog:supplier_delete", kwargs={"pk": sup.pk})
        )
        assert resp.status_code == 302
        assert Supplier.objects.filter(pk=sup.pk).count() == 0
        assert Supplier.all_objects.filter(pk=sup.pk).count() == 1


class TestProductViews:
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Keyboards")

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(company_name="Logitech")

    def test_product_list_view(self, admin_client, category, supplier):
        Product.objects.create(
            sku="LOGI-MX-KEYS",
            name="MX Keys",
            category=category,
            supplier=supplier,
            purchase_price=8000.00,
            selling_price=10000.00
        )
        resp = admin_client.get(reverse("catalog:product_list"))
        assert resp.status_code == 200
        assert b"MX Keys" in resp.content
        assert b"LOGI-MX-KEYS" in resp.content

    def test_product_create_view(self, admin_client, category, supplier):
        resp = admin_client.post(
            reverse("catalog:product_add"),
            {
                "sku": "LOGI-MX-KEYS",
                "name": "MX Keys",
                "category": str(category.pk),
                "supplier": str(supplier.pk),
                "purchase_price": "8000.00",
                "selling_price": "10000.00",
                "minimum_stock": 5,
                "unit": "PCS",
                "is_active": True,
            }
        )
        assert resp.status_code == 302
        assert Product.objects.filter(sku="LOGI-MX-KEYS").exists()

    def test_product_create_validation_error(self, admin_client, category, supplier):
        # Selling price is less than purchase price
        resp = admin_client.post(
            reverse("catalog:product_add"),
            {
                "sku": "LOGI-MX-KEYS",
                "name": "MX Keys",
                "category": str(category.pk),
                "supplier": str(supplier.pk),
                "purchase_price": "10000.00",
                "selling_price": "8000.00",
                "minimum_stock": 5,
                "unit": "PCS",
                "is_active": True,
            }
        )
        assert resp.status_code == 200
        assert b"Selling price must be greater than or equal to purchase price." in resp.content
        assert not Product.objects.filter(sku="LOGI-MX-KEYS").exists()

    def test_product_detail_view(self, admin_client, category, supplier):
        prod = Product.objects.create(
            sku="LOGI-MX-KEYS",
            name="MX Keys",
            category=category,
            supplier=supplier,
            purchase_price=8000.00,
            selling_price=10000.00
        )
        resp = admin_client.get(reverse("catalog:product_detail", kwargs={"pk": prod.pk}))
        assert resp.status_code == 200
        assert b"MX Keys" in resp.content
        assert b"LOGI-MX-KEYS" in resp.content
        assert b"Keyboards" in resp.content

    def test_product_update_view(self, admin_client, category, supplier):
        prod = Product.objects.create(
            sku="LOGI-MX-KEYS",
            name="MX Keys",
            category=category,
            supplier=supplier,
            purchase_price=8000.00,
            selling_price=10000.00
        )
        resp = admin_client.post(
            reverse("catalog:product_edit", kwargs={"pk": prod.pk}),
            {
                "sku": "LOGI-MX-KEYS-V2",
                "name": "MX Keys Advanced",
                "category": str(category.pk),
                "supplier": str(supplier.pk),
                "purchase_price": "8500.00",
                "selling_price": "11000.00",
                "minimum_stock": 5,
                "unit": "PCS",
                "is_active": True,
            }
        )
        assert resp.status_code == 302
        prod.refresh_from_db()
        assert prod.sku == "LOGI-MX-KEYS-V2"
        assert prod.name == "MX Keys Advanced"

    def test_product_delete_view(self, admin_client, category, supplier):
        prod = Product.objects.create(
            sku="LOGI-MX-KEYS",
            name="MX Keys",
            category=category,
            supplier=supplier,
            purchase_price=8000.00,
            selling_price=10000.00
        )
        resp = admin_client.post(
            reverse("catalog:product_delete", kwargs={"pk": prod.pk})
        )
        assert resp.status_code == 302
        assert Product.objects.filter(pk=prod.pk).count() == 0
        assert Product.all_objects.filter(pk=prod.pk).count() == 1
