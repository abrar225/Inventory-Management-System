import csv
import io

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.purchasing.services import PurchasingService
from apps.sales.services import SalesService

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data():
    user = UserFactory()
    # Add view permission
    view_perm = Permission.objects.get(codename="view_product")
    user.user_permissions.add(view_perm)

    supplier = Supplier.objects.create(
        company_name="Rep Supplier",
        contact_person="Michael Scott",
        email="michael@rep.com",
        phone="1234567890",
        address="100 Pap St",
        city="Scranton",
        state="PA",
        postal_code="18501",
        country="USA",
        created_by=user,
        updated_by=user,
    )
    category = Category.objects.create(
        name="Rep Category",
        slug="rep-category",
        created_by=user,
        updated_by=user,
    )
    product = Product.objects.create(
        name="Rep Product",
        sku="REP-PROD-99",
        category=category,
        supplier=supplier,
        purchase_price=10.00,
        selling_price=15.00,
        current_stock=20,
        minimum_stock=5,
        created_by=user,
        updated_by=user,
    )
    return {
        "user": user,
        "product": product,
        "category": category,
        "supplier": supplier,
    }


def test_reports_dashboard_view_aggregations(client, setup_data):
    """Verifies report dashboard returns 200 and aggregates cost/revenue correctly."""
    user = setup_data["user"]
    client.force_login(user)

    url = reverse("reporting:dashboard")
    response = client.get(url)
    assert response.status_code == 200

    context = response.context
    # Assert Inventory valuation totals (20 items * ₹10 purchase_price = 200 cost)
    assert context["inv_total_qty"] == 20
    assert context["inv_cost_valuation"] == 200.00
    assert context["inv_retail_valuation"] == 300.00  # 20 * ₹15
    assert context["inv_potential_profit"] == 100.00


def test_sales_and_purchases_report_with_data(client, setup_data):
    """Verifies date filters pull correct sales invoices and PO items."""
    user = setup_data["user"]
    client.force_login(user)

    # 1. Add some sales data
    SalesService.create_sale(
        customer_name="Test Customer",
        sale_date="2026-07-19",
        items_data=[{"product": setup_data["product"], "quantity": 5, "unit_price": 15.00}],
        user=user,
    )

    # 2. Add received purchase order data
    purchase = PurchasingService.create_purchase(
        supplier=setup_data["supplier"],
        purchase_date="2026-07-19",
        items_data=[{"product": setup_data["product"], "quantity": 10, "unit_price": 10.00}],
        user=user,
    )
    PurchasingService.receive_purchase(purchase, user)

    url = reverse("reporting:dashboard")
    response = client.get(url)
    assert response.status_code == 200

    context = response.context
    assert context["sales_qty"] == 5
    assert context["sales_revenue"] == 75.00  # 5 * 15.00
    assert context["purchases_qty"] == 10
    assert context["purchases_cost"] == 100.00  # 10 * 10.00


def test_inventory_valuation_csv_export(client, setup_data):
    """Verifies that inventory CSV contains headers and product row records."""
    user = setup_data["user"]
    client.force_login(user)

    url = reverse("reporting:inventory_csv")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    # Decode CSV content and parse
    csv_content = response.content.decode("utf-8")
    csv_file = io.StringIO(csv_content)
    reader = csv.reader(csv_file)
    rows = list(reader)

    # Assert headers
    assert rows[0] == [
        "SKU",
        "Product Name",
        "Category",
        "Current Stock",
        "Unit",
        "Purchase Price (₹)",
        "Selling Price (₹)",
        "Cost Valuation (₹)",
        "Retail Valuation (₹)",
        "Potential Profit (₹)",
    ]
    # Assert row values
    assert rows[1][0] == "REP-PROD-99"
    assert rows[1][1] == "Rep Product"
    assert rows[1][3] == "20"


def test_sales_report_csv_export(client, setup_data):
    """Verifies that sales CSV export retrieves transactions correctly."""
    user = setup_data["user"]
    client.force_login(user)

    SalesService.create_sale(
        customer_name="CSV Customer",
        sale_date="2026-07-19",
        items_data=[
            {"product": setup_data["product"], "quantity": 3, "unit_price": 15.00}
        ],
        user=user,
    )

    url = reverse("reporting:sales_csv")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    csv_content = response.content.decode("utf-8")
    assert "CSV Customer" in csv_content
    assert "REP-PROD-99" in csv_content


def test_purchases_report_csv_export(client, setup_data):
    """Verifies that purchases CSV export retrieves received orders correctly."""
    user = setup_data["user"]
    client.force_login(user)

    purchase = PurchasingService.create_purchase(
        supplier=setup_data["supplier"],
        purchase_date="2026-07-19",
        items_data=[
            {"product": setup_data["product"], "quantity": 7, "unit_price": 10.00}
        ],
        user=user,
    )
    PurchasingService.receive_purchase(purchase, user)

    url = reverse("reporting:purchases_csv")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    csv_content = response.content.decode("utf-8")
    assert "Rep Supplier" in csv_content
    assert "REP-PROD-99" in csv_content

