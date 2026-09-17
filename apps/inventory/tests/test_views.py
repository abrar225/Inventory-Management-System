import pytest
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockAdjustment, StockMovement

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    admin_user = UserFactory(is_superuser=True, is_staff=True)
    client.login(username=admin_user.email, password="password123!")
    return client


class TestInventoryViews:
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Laptops")

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(company_name="Dell")

    @pytest.fixture
    def product(self, category, supplier):
        return Product.objects.create(
            sku="DELL-XPS-13",
            name="Dell XPS 13",
            category=category,
            supplier=supplier,
            purchase_price=80000.00,
            selling_price=95000.00,
            current_stock=10,
        )

    def test_inventory_dashboard_view(self, admin_client, product):
        resp = admin_client.get(reverse("inventory:dashboard"))
        assert resp.status_code == 200
        assert b"Dell XPS 13" in resp.content
        assert b"DELL-XPS-13" in resp.content
        assert b"10" in resp.content
        assert b"Inventory Value" in resp.content

    def test_stock_movement_list_view(self, admin_client, product):
        user = UserFactory()
        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            reference_type=StockMovement.ReferenceType.ADJUSTMENT,
            quantity=-2,
            balance_after=8,
            reason="Damaged unit",
            created_by=user,
        )
        resp = admin_client.get(reverse("inventory:movement_list"))
        assert resp.status_code == 200
        assert b"Dell XPS 13" in resp.content
        assert b"Adjustment" in resp.content
        assert b"-2" in resp.content

    def test_stock_adjustment_create_view_get(self, admin_client, product):
        resp = admin_client.get(reverse("inventory:adjust_stock"))
        assert resp.status_code == 200
        assert b"Submit Adjustment" in resp.content

    def test_stock_adjustment_create_view_post_success(self, admin_client, product):
        resp = admin_client.post(
            reverse("inventory:adjust_stock"),
            {
                "product": str(product.id),
                "adjustment_type": StockAdjustment.AdjustmentType.INCREASE,
                "quantity": 5,
                "reason": "New stock added",
            },
        )
        assert resp.status_code == 302
        product.refresh_from_db()
        assert product.current_stock == 15
        assert StockAdjustment.objects.filter(reason="New stock added").exists()

    def test_stock_adjustment_create_view_post_insufficient_error(
        self, admin_client, product
    ):
        resp = admin_client.post(
            reverse("inventory:adjust_stock"),
            {
                "product": str(product.id),
                "adjustment_type": StockAdjustment.AdjustmentType.DECREASE,
                "quantity": 15,
                "reason": "Shrinkage",
            },
        )
        assert resp.status_code == 200
        assert b"Insufficient stock for Dell XPS 13" in resp.content
        product.refresh_from_db()
        assert product.current_stock == 10
