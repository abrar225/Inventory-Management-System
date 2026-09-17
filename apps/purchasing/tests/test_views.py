import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.purchasing.models import Purchase

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data():
    user = UserFactory()
    # Grant permissions
    view_perm = Permission.objects.get(codename="view_purchase")
    add_perm = Permission.objects.get(codename="add_purchase")
    change_perm = Permission.objects.get(codename="change_purchase")
    user.user_permissions.add(view_perm, add_perm, change_perm)

    supplier = Supplier.objects.create(
        company_name="Delta Supplies",
        contact_person="Dwight Schrute",
        email="dwight@delta.com",
        phone="555-0300",
        address="300 Beet Farm Way",
        city="Scranton",
        state="PA",
        postal_code="18502",
        country="USA",
        created_by=user,
        updated_by=user,
    )
    category = Category.objects.create(
        name="Office Supplies",
        slug="office-supplies",
        created_by=user,
        updated_by=user,
    )
    product = Product.objects.create(
        name="Premium Paper Reams",
        sku="PAPER-PREM-1",
        category=category,
        supplier=supplier,
        purchase_price=200.00,
        selling_price=300.00,
        current_stock=20,
        minimum_stock=10,
        created_by=user,
        updated_by=user,
    )
    return {
        "user": user,
        "supplier": supplier,
        "product": product,
    }


def test_purchase_list_view(client, setup_data):
    """Verifies that the purchase order list page displays correct items."""
    user = setup_data["user"]
    client.force_login(user)

    purchase = Purchase.objects.create(
        purchase_number="PO-LIST-VIEW-1",
        supplier=setup_data["supplier"],
        purchase_date="2026-07-18",
        created_by=user,
        updated_by=user,
    )

    url = reverse("purchasing:purchase_list")
    response = client.get(url)
    assert response.status_code == 200
    assert purchase.purchase_number in response.content.decode()


def test_purchase_detail_view(client, setup_data):
    """Verifies that the details page shows supplier and meta information."""
    user = setup_data["user"]
    client.force_login(user)

    purchase = Purchase.objects.create(
        purchase_number="PO-DETAIL-VIEW-1",
        supplier=setup_data["supplier"],
        purchase_date="2026-07-18",
        created_by=user,
        updated_by=user,
    )

    url = reverse("purchasing:purchase_detail", args=[purchase.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "Delta Supplies" in response.content.decode()


def test_purchase_create_view_with_formset(client, setup_data):
    """Verifies dynamic formset PO creation returns success and redirects."""
    user = setup_data["user"]
    client.force_login(user)

    url = reverse("purchasing:purchase_add")
    post_data = {
        "supplier": str(setup_data["supplier"].id),
        "purchase_date": "2026-07-18",
        "tax": "15.00",
        "discount": "5.00",
        "notes": "Testing formset create",

        # Management form
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",

        # Line item index 0
        "items-0-product": str(setup_data["product"].id),
        "items-0-quantity": "10",
        "items-0-unit_price": "25.00",
    }

    response = client.post(url, post_data)
    assert response.status_code == 302  # redirects to detail page

    # Assert DB counts
    assert Purchase.objects.filter(notes="Testing formset create").exists()
    purchase = Purchase.objects.get(notes="Testing formset create")
    assert purchase.items.count() == 1
    assert purchase.items.first().quantity == 10


def test_purchase_receive_action_view(client, setup_data):
    """Verifies receive PO POST view receiving trigger and redirects."""
    user = setup_data["user"]
    client.force_login(user)

    purchase = Purchase.objects.create(
        purchase_number="PO-RECEIVE-VIEW-1",
        supplier=setup_data["supplier"],
        purchase_date="2026-07-18",
        status=Purchase.Status.ORDERED,
        created_by=user,
        updated_by=user,
    )

    url = reverse("purchasing:purchase_receive", args=[purchase.pk])
    response = client.post(url)
    assert response.status_code == 302

    purchase.refresh_from_db()
    assert purchase.status == Purchase.Status.RECEIVED
