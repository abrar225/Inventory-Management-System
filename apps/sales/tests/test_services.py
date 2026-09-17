import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockMovement
from apps.inventory.services import InsufficientStockError
from apps.sales.models import Sale
from apps.sales.services import SalesService

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_data():
    user = UserFactory()
    supplier = Supplier.objects.create(
        company_name="Gamma Supply Hub",
        contact_person="Michael Scott",
        email="michael@gamma.com",
        phone="555-0400",
        address="400 Dunder St",
        city="Scranton",
        state="PA",
        postal_code="18503",
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
        name="Laptop Pro 15",
        sku="LAP-PRO-15",
        category=category,
        supplier=supplier,
        purchase_price=800.00,
        selling_price=1200.00,
        current_stock=8,
        minimum_stock=2,
        created_by=user,
        updated_by=user,
    )
    return {
        "user": user,
        "product": product,
    }


def test_create_sale_successful_stock_reduction(test_data):
    """Verifies that create_sale correctly records sales and decreases stock."""
    user = test_data["user"]
    product = test_data["product"]

    assert product.current_stock == 8

    items_data = [
        {
            "product": product,
            "quantity": 3,
            "unit_price": 1200.00,
        }
    ]

    sale = SalesService.create_sale(
        customer_name="Acme Corp",
        sale_date="2026-07-18",
        items_data=items_data,
        user=user,
        tax=100.00,
        discount=50.00,
    )

    assert sale.invoice_number.startswith("INV-")
    assert sale.status == Sale.Status.COMPLETED
    assert sale.subtotal == 3600.00
    assert sale.grand_total == 3650.00  # 3600 + 100 - 50

    # Reload product and assert stock deduction
    product.refresh_from_db()
    assert product.current_stock == 5  # 8 - 3

    # Assert stock movement ledger entry
    movement = StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE
    ).first()

    assert movement is not None
    assert movement.quantity == -3
    assert movement.balance_after == 5
    assert movement.reference_type == StockMovement.ReferenceType.SALE
    assert movement.reference_id == sale.id


def test_create_sale_insufficient_stock_error(test_data):
    """Verifies that create_sale fails and rolls back when quantity > stock."""
    user = test_data["user"]
    product = test_data["product"]

    assert product.current_stock == 8

    # Requesting 10 items when only 8 exist
    items_data = [
        {
            "product": product,
            "quantity": 10,
            "unit_price": 1200.00,
        }
    ]

    with pytest.raises(InsufficientStockError) as exc_info:
        SalesService.create_sale(
            customer_name="Overbuy Inc",
            sale_date="2026-07-18",
            items_data=items_data,
            user=user,
        )

    # Check error details
    assert "Insufficient stock for Laptop Pro 15" in str(exc_info.value)

    # Ensure transaction rolled back: stock unchanged and no Sale created
    product.refresh_from_db()
    assert product.current_stock == 8
    assert not Sale.objects.filter(customer_name="Overbuy Inc").exists()
