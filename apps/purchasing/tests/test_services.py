import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockMovement
from apps.purchasing.models import Purchase
from apps.purchasing.services import PurchasingService

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_data():
    user = UserFactory()
    supplier = Supplier.objects.create(
        company_name="Beta Distributors",
        contact_person="Bob Vance",
        email="bob@betadist.com",
        phone="555-0211",
        address="200 Warehouse Rd",
        city="Scranton",
        state="PA",
        postal_code="18501",
        country="USA",
        created_by=user,
        updated_by=user,
    )
    category = Category.objects.create(
        name="Electronics",
        slug="electronics",
        created_by=user,
        updated_by=user,
    )
    product = Product.objects.create(
        name="Smartphone X",
        sku="SMART-X-1",
        category=category,
        supplier=supplier,
        purchase_price=15000.00,
        selling_price=20000.00,
        current_stock=10,
        minimum_stock=5,
        created_by=user,
        updated_by=user,
    )
    return {
        "user": user,
        "supplier": supplier,
        "product": product,
    }


def test_create_purchase_order(test_data):
    """Verifies that create_purchase creates records and totals correctly."""
    user = test_data["user"]
    supplier = test_data["supplier"]
    product = test_data["product"]

    items_data = [
        {
            "product": product,
            "quantity": 15,
            "unit_price": 500.00,
        }
    ]

    purchase = PurchasingService.create_purchase(
        supplier=supplier,
        purchase_date="2026-07-18",
        items_data=items_data,
        user=user,
        tax=75.00,
        discount=50.00,
        notes="Urgent delivery requested.",
    )

    assert purchase.purchase_number.startswith("PO-")
    assert purchase.status == Purchase.Status.ORDERED
    assert purchase.subtotal == 7500.00  # 15 * 500
    assert purchase.grand_total == 7525.00  # 7500 + 75 - 50
    assert purchase.items.count() == 1

    item = purchase.items.first()
    assert item.product == product
    assert item.quantity == 15
    assert item.unit_price == 500.00
    assert item.line_total == 7500.00


def test_receive_purchase_order_stock_addition(test_data):
    """Verifies receiving a PO increases stock and logs ledger movement."""
    user = test_data["user"]
    supplier = test_data["supplier"]
    product = test_data["product"]

    items_data = [
        {
            "product": product,
            "quantity": 5,
            "unit_price": 400.00,
        }
    ]

    # Initialize current stock to 10
    assert product.current_stock == 10

    purchase = PurchasingService.create_purchase(
        supplier=supplier,
        purchase_date="2026-07-18",
        items_data=items_data,
        user=user,
    )

    # Perform receipt
    received_purchase = PurchasingService.receive_purchase(purchase, user)

    assert received_purchase.status == Purchase.Status.RECEIVED

    # Reload product from db and confirm stock update
    product.refresh_from_db()
    assert product.current_stock == 15  # 10 + 5

    # Check ledger StockMovement entry
    movement = StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.PURCHASE
    ).first()

    assert movement is not None
    assert movement.quantity == 5
    assert movement.balance_after == 15
    assert movement.reference_type == StockMovement.ReferenceType.PURCHASE
    assert movement.reference_id == purchase.id
