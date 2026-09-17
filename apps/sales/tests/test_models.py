import pytest

from apps.accounts.tests.factories import UserFactory
from apps.sales.models import Sale

pytestmark = pytest.mark.django_db


def test_sale_model_string_representation():
    """Verifies the string output format for the Sale header model."""
    user = UserFactory()
    sale = Sale.objects.create(
        invoice_number="INV-TEST-9988",
        customer_name="Jane Doe",
        sale_date="2026-07-18",
        subtotal=120.00,
        tax=10.00,
        discount=5.00,
        grand_total=125.00,
        status=Sale.Status.COMPLETED,
        created_by=user,
        updated_by=user,
    )
    assert str(sale) == "INV-TEST-9988 - Jane Doe (Completed)"
