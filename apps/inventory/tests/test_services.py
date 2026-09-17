import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockAdjustment, StockMovement
from apps.inventory.services import InsufficientStockError, InventoryService

pytestmark = pytest.mark.django_db


class TestInventoryService:
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

    def test_adjust_stock_increase(self, product, user):
        adj = InventoryService.adjust_stock(
            product=product,
            quantity=5,
            adjustment_type=StockAdjustment.AdjustmentType.INCREASE,
            reason="Received extra units",
            created_by=user,
        )
        product.refresh_from_db()
        assert product.current_stock == 15
        assert adj.quantity == 5
        assert adj.adjustment_type == StockAdjustment.AdjustmentType.INCREASE

        # Verify ledger
        movement = StockMovement.objects.get(reference_id=adj.id)
        assert movement.quantity == 5
        assert movement.balance_after == 15
        assert movement.movement_type == StockMovement.MovementType.ADJUSTMENT

    def test_adjust_stock_decrease(self, product, user):
        adj = InventoryService.adjust_stock(
            product=product,
            quantity=3,
            adjustment_type=StockAdjustment.AdjustmentType.DAMAGE,
            reason="Broken screen",
            created_by=user,
        )
        product.refresh_from_db()
        assert product.current_stock == 7
        assert adj.quantity == 3

        # Verify ledger
        movement = StockMovement.objects.get(reference_id=adj.id)
        assert movement.quantity == -3
        assert movement.balance_after == 7

    def test_adjust_stock_insufficient(self, product, user):
        with pytest.raises(InsufficientStockError):
            InventoryService.adjust_stock(
                product=product,
                quantity=12,
                adjustment_type=StockAdjustment.AdjustmentType.LOST,
                reason="Theft",
                created_by=user,
            )
        product.refresh_from_db()
        assert product.current_stock == 10  # unchanged due to atomic rollback

    def test_reconcile_stock(self, product, user):
        adj = InventoryService.reconcile_stock(
            product=product,
            expected_quantity=4,
            reason="Monthly cycle count",
            created_by=user,
        )
        product.refresh_from_db()
        assert product.current_stock == 4
        assert adj.adjustment_type == StockAdjustment.AdjustmentType.CORRECTION
        assert adj.quantity == 6  # discrepancy magnitude

    def test_record_movement(self, product, user):
        mov = InventoryService.record_movement(
            product=product,
            quantity=5,
            movement_type=StockMovement.MovementType.PURCHASE,
            reference_type=StockMovement.ReferenceType.PURCHASE,
            reference_id=None,
            reason="Purchase Order #1",
            created_by=user,
        )
        product.refresh_from_db()
        assert product.current_stock == 15
        assert mov.quantity == 5
        assert mov.balance_after == 15
