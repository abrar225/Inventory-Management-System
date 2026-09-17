import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.accounts.models import Role, User
from apps.accounts.tests.factories import RoleFactory, UserFactory
from apps.catalog.models import Category, Product, Supplier
from apps.common.templatetags.common_extras import get_low_stock_alerts

pytestmark = pytest.mark.django_db


class TestUserManagementViews:
    def test_user_list_admin_only(self, client):
        # Authenticated as staff/non-admin
        staff_user = UserFactory(role=RoleFactory(name=Role.Name.SALES_STAFF))
        client.login(username=staff_user.email, password="password123!")

        resp = client.get(reverse("accounts:user_list"))
        assert resp.status_code == 403

        # Authenticated as admin
        admin_user = UserFactory(role=RoleFactory(name=Role.Name.ADMINISTRATOR))
        client.login(username=admin_user.email, password="password123!")

        resp = client.get(reverse("accounts:user_list"))
        assert resp.status_code == 200
        assert admin_user.email.encode() in resp.content

    def test_user_create_admin(self, client):
        admin_user = UserFactory(role=RoleFactory(name=Role.Name.ADMINISTRATOR))
        client.login(username=admin_user.email, password="password123!")

        resp = client.get(reverse("accounts:user_add"))
        assert resp.status_code == 200

        # Post valid user creation
        role = RoleFactory(name=Role.Name.INVENTORY_MANAGER)
        post_data = {
            "email": "new_manager@example.com",
            "username": "new_manager",
            "first_name": "New",
            "last_name": "Manager",
            "phone": "+919876543210",
            "role": str(role.id),
            "password": "strongPassword123!",
            "is_active": "on",
        }

        resp = client.post(reverse("accounts:user_add"), post_data)
        assert resp.status_code == 302
        assert resp.url == reverse("accounts:user_list")

        new_user = User.objects.get(email="new_manager@example.com")
        assert new_user.first_name == "New"
        assert new_user.role == role
        # Check matching group is assigned
        group = Group.objects.get(name=Role.Name.INVENTORY_MANAGER)
        assert group in new_user.groups.all()

    def test_user_update_admin(self, client):
        admin_user = UserFactory(role=RoleFactory(name=Role.Name.ADMINISTRATOR))
        client.login(username=admin_user.email, password="password123!")

        staff_role = RoleFactory(name=Role.Name.SALES_STAFF)
        target_user = UserFactory(role=staff_role, email="staff@example.com")

        resp = client.get(reverse("accounts:user_update", args=[target_user.pk]))
        assert resp.status_code == 200

        # Change role to Administrator
        admin_role = Role.objects.get(name=Role.Name.ADMINISTRATOR)
        post_data = {
            "email": "staff_promoted@example.com",
            "username": "staff",
            "first_name": "Staff",
            "last_name": "Promoted",
            "phone": "555-5555",
            "role": str(admin_role.id),
            "is_active": "on",
            "password": "",  # Blank means password stays unchanged
        }

        resp = client.post(
            reverse("accounts:user_update", args=[target_user.pk]), post_data
        )
        assert resp.status_code == 302

        target_user.refresh_from_db()
        assert target_user.email == "staff_promoted@example.com"
        assert target_user.role == admin_role
        assert target_user.check_password("password123!")  # Check original password preserved


class TestLowStockAlertTag:
    def test_low_stock_alerts_filter(self):
        supplier = Supplier.objects.create(company_name="Supplier A")
        category = Category.objects.create(name="Electronics")

        # 1. Product above threshold
        Product.objects.create(
            name="iPhone 15",
            sku="IPH15",
            category=category,
            supplier=supplier,
            current_stock=10,
            minimum_stock=5,
            unit="pcs",
            purchase_price=100.00,
            selling_price=150.00,
        )

        # 2. Product at threshold (should trigger)
        low_p1 = Product.objects.create(
            name="MacBook Air",
            sku="MBAIR",
            category=category,
            supplier=supplier,
            current_stock=2,
            minimum_stock=2,
            unit="pcs",
            purchase_price=1000.00,
            selling_price=1500.00,
        )

        # 3. Product below threshold (should trigger)
        low_p2 = Product.objects.create(
            name="USB-C Cable",
            sku="USBC",
            category=category,
            supplier=supplier,
            current_stock=1,
            minimum_stock=10,
            unit="pcs",
            purchase_price=5.00,
            selling_price=10.00,
        )

        alerts = get_low_stock_alerts()
        assert len(alerts) == 2
        assert low_p1 in alerts
        assert low_p2 in alerts
