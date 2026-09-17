import pytest
from django.core.management import call_command

from apps.catalog.models import Product

pytestmark = pytest.mark.django_db


def test_seed_demo_data_command():
    """Verify that the seed_demo_data command runs successfully and is idempotent."""
    # First invocation: populates the empty database
    call_command("seed_demo_data")
    assert Product.objects.count() == 8

    # Second invocation: handles existing items gracefully without duplicates or key errors
    call_command("seed_demo_data")
    assert Product.objects.count() == 8
