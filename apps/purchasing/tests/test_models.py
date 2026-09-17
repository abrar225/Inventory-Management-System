import pytest

from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Supplier
from apps.purchasing.models import Purchase

pytestmark = pytest.mark.django_db


def test_purchase_model_string_representation():
    """Verifies the string output format for the Purchase header model."""
    user = UserFactory()
    supplier = Supplier.objects.create(
        company_name="Alpha Tech Corp",
        contact_person="Alice Smith",
        email="alice@alphatech.com",
        phone="555-0199",
        address="100 Tech Blvd",
        city="Austin",
        state="TX",
        postal_code="78701",
        country="USA",
        created_by=user,
        updated_by=user,
    )
    purchase = Purchase.objects.create(
        purchase_number="PO-TEST-12345",
        supplier=supplier,
        purchase_date="2026-07-18",
        subtotal=250.00,
        tax=20.00,
        discount=10.00,
        grand_total=260.00,
        status=Purchase.Status.DRAFT,
        created_by=user,
        updated_by=user,
    )
    assert str(purchase) == "PO-TEST-12345 - Alpha Tech Corp (Draft)"
