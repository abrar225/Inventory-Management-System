import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.sales.models import Sale

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data():
    user = UserFactory()
    # Grant permissions
    view_perm = Permission.objects.get(codename="view_sale")
    add_perm = Permission.objects.get(codename="add_sale")
    user.user_permissions.add(view_perm, add_perm)

    supplier = Supplier.objects.create(
        company_name="Dunder Mifflin",
        contact_person="Dwight Schrute",
        email="dwight@dundermifflin.com",
        phone="555-0450",
        address="1725 Slough Ave",
        city="Scranton",
        state="PA",
        postal_code="18505",
        country="USA",
        created_by=user,
        updated_by=user,
    )
    category = Category.objects.create(
        name="Paper Products",
        slug="paper-products",
        created_by=user,
        updated_by=user,
    )
    product = Product.objects.create(
        name="Weyerhaeuser Paper Reams",
        sku="PAPER-WEY-1",
        category=category,
        supplier=supplier,
        purchase_price=8.00,
        selling_price=10.00,
        current_stock=100,
        minimum_stock=20,
        created_by=user,
        updated_by=user,
    )
    return {
        "user": user,
        "product": product,
    }


def test_sale_list_view(client, setup_data):
    """Verifies that the sales list page displays correct items."""
    user = setup_data["user"]
    client.force_login(user)

    sale = Sale.objects.create(
        invoice_number="INV-LIST-VIEW-1",
        customer_name="Andy Bernard",
        sale_date="2026-07-18",
        created_by=user,
        updated_by=user,
    )

    url = reverse("sales:sale_list")
    response = client.get(url)
    assert response.status_code == 200
    assert sale.invoice_number in response.content.decode()


def test_sale_detail_view(client, setup_data):
    """Verifies that the sale invoice page shows customer information."""
    user = setup_data["user"]
    client.force_login(user)

    sale = Sale.objects.create(
        invoice_number="INV-DETAIL-VIEW-1",
        customer_name="Pam Beesly",
        sale_date="2026-07-18",
        created_by=user,
        updated_by=user,
    )

    url = reverse("sales:sale_detail", args=[sale.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "Pam Beesly" in response.content.decode()


def test_sale_create_view_with_formset(client, setup_data):
    """Verifies dynamic formset Sale creation deducts stock and redirects."""
    user = setup_data["user"]
    client.force_login(user)

    url = reverse("sales:sale_add")
    post_data = {
        "customer_name": "Dunder Mifflin Client",
        "sale_date": "2026-07-18",
        "tax": "5.00",
        "discount": "2.00",

        # Management form
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",

        # Line item index 0
        "items-0-product": str(setup_data["product"].id),
        "items-0-quantity": "10",
        "items-0-unit_price": "10.00",
    }

    response = client.post(url, post_data)
    assert response.status_code == 302  # redirects to invoice details page

    # Assert DB counts
    assert Sale.objects.filter(customer_name="Dunder Mifflin Client").exists()
    sale = Sale.objects.get(customer_name="Dunder Mifflin Client")
    assert sale.items.count() == 1
    assert sale.items.first().quantity == 10

    # Assert stock deduction
    setup_data["product"].refresh_from_db()
    assert setup_data["product"].current_stock == 90  # 100 - 10


def test_sale_create_insufficient_stock_returns_form_error(client, setup_data):
    """Verifies over-purchasing stock yields model validation error messages."""
    user = setup_data["user"]
    client.force_login(user)

    url = reverse("sales:sale_add")
    post_data = {
        "customer_name": "Too Greedy Client",
        "sale_date": "2026-07-18",
        "tax": "0.00",
        "discount": "0.00",

        # Management form
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",

        # Line item index 0 (requesting 200 reams, but only 100 in stock)
        "items-0-product": str(setup_data["product"].id),
        "items-0-quantity": "200",
        "items-0-unit_price": "10.00",
    }

    response = client.post(url, post_data)
    assert response.status_code == 200  # stays on the form page due to errors
    assert "Insufficient stock for Weyerhaeuser Paper Reams" in response.content.decode()
