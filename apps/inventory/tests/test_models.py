import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockAdjustment, StockMovement

pytestmark = pytest.mark.django_db


class TestInventoryModels:
    @pytest.fixture
    def user(self):
        return UserFactory()

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

    def test_stock_movement_creation(self, product, user):
        movement = StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            reference_type=StockMovement.ReferenceType.ADJUSTMENT,
            quantity=-5,
            balance_after=5,
            reason="Damaged stock",
            created_by=user,
        )
        assert movement.quantity == -5
        assert movement.balance_after == 5
        assert "ADJUSTMENT" in str(movement)

    def test_stock_adjustment_creation(self, product, user):
        adjustment = StockAdjustment.objects.create(
            product=product,
            adjustment_type=StockAdjustment.AdjustmentType.DAMAGE,
            quantity=5,
            reason="Water damage",
            created_by=user,
        )
        assert adjustment.quantity == 5
        assert str(adjustment) == f"{product.name} - Damage of 5"
