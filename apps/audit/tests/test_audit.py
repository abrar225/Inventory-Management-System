import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role
from apps.accounts.tests.factories import RoleFactory, UserFactory
from apps.audit.models import AuditLog
from apps.audit.services import AuditService
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.services import InventoryService
from apps.purchasing.models import Purchase
from apps.purchasing.services import PurchasingService
from apps.sales.services import SalesService

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestAuditLogging:
    def test_audit_service_log(self):
        user = UserFactory(email="actor@example.com")
        log = AuditService.log(
            user=user,
            action="Test Action",
            model_name="Product",
            object_id="1234-5678",
            object_repr="Gizmo",
            details="Created a fancy gizmo.",
            ip_address="127.0.0.1",
        )

        assert log.user == user
        assert log.action == "Test Action"
        assert log.model_name == "Product"
        assert log.object_id == "1234-5678"
        assert log.object_repr == "Gizmo"
        assert log.details == "Created a fancy gizmo."
        assert log.ip_address == "127.0.0.1"

    def test_auth_signals_log_login_logout(self, client):
        user = UserFactory(email="signaler@example.com", password="password123!")

        # Verify login logs an audit record
        resp = client.post(
            reverse("accounts:login"),
            {"username": "signaler@example.com", "password": "password123!"},
        )
        assert resp.status_code == 302

        # Check audit log entry
        login_log = AuditLog.objects.filter(user=user, action="Login").first()
        assert login_log is not None
        assert "logged in" in login_log.details

        # Verify logout logs an audit record
        resp = client.post(reverse("accounts:logout"))
        assert resp.status_code == 302

        logout_log = AuditLog.objects.filter(user=user, action="Logout").first()
        assert logout_log is not None
        assert "logged out" in logout_log.details

    def test_business_services_write_audit_logs(self):
        admin_user = UserFactory(role=RoleFactory(name=Role.Name.ADMINISTRATOR))
        category = Category.objects.create(name="Tech")
        supplier = Supplier.objects.create(company_name="Supplier A")
        product = Product.objects.create(
            name="Tablet",
            sku="TAB1",
            category=category,
            supplier=supplier,
            current_stock=10,
            minimum_stock=2,
            unit="pcs",
            purchase_price=100.00,
            selling_price=150.00,
        )

        # 1. Stock Adjustment Audit Log
        InventoryService.adjust_stock(
            product=product,
            quantity=5,
            adjustment_type="Increase",
            reason="Found on shelf",
            created_by=admin_user,
        )
        adj_log = AuditLog.objects.filter(action="Stock Adjustment").first()
        assert adj_log is not None
        assert adj_log.user == admin_user
        assert "Found on shelf" in adj_log.details

        # 2. Purchasing PO Receipt Audit Log
        purchase = Purchase.objects.create(
            supplier=supplier,
            purchase_number="PO-9999",
            status=Purchase.Status.DRAFT,
            created_by=admin_user,
            purchase_date=timezone.now().date(),
        )
        purchase.items.create(product=product, quantity=5, unit_price=10.00)
        # Transition draft to order first
        purchase.status = Purchase.Status.ORDERED
        purchase.save()

        PurchasingService.receive_purchase(purchase, user=admin_user)
        po_log = AuditLog.objects.filter(action="Receive Purchase Order").first()
        assert po_log is not None
        assert po_log.object_repr == "PO-9999"

        # 3. Sales Invoice Audit Log
        items_data = [{"product": product, "quantity": 2, "unit_price": 20.00}]
        SalesService.create_sale(
            customer_name="John Doe",
            items_data=items_data,
            tax=0.00,
            discount=0.00,
            sale_date=timezone.now().date(),
            user=admin_user,
        )
        sales_log = AuditLog.objects.filter(action="Complete Sale").first()
        assert sales_log is not None
        assert "John Doe" in sales_log.details


class TestAuditViews:
    def test_audit_list_admin_only(self, client):
        non_admin = UserFactory(role=RoleFactory(name=Role.Name.SALES_STAFF))
        client.login(username=non_admin.email, password="password123!")

        resp = client.get(reverse("audit:logs"))
        assert resp.status_code == 403

        admin_user = UserFactory(role=RoleFactory(name=Role.Name.ADMINISTRATOR))
        client.login(username=admin_user.email, password="password123!")

        # Create some audit log entries
        AuditService.log(user=admin_user, action="Delete Item", details="Wiped product.")
        AuditService.log(user=admin_user, action="Reset Password", details="Reset admin.")

        resp = client.get(reverse("audit:logs"))
        assert resp.status_code == 200
        assert b"System Audit Logs" in resp.content
        assert b"Delete Item" in resp.content
        assert b"Reset Password" in resp.content

        # Test search query
        resp_search = client.get(reverse("audit:logs") + "?q=Wiped")
        assert resp_search.status_code == 200
        assert b"Wiped product." in resp_search.content
        assert b"Reset admin." not in resp_search.content

        # Test action filter
        resp_filter = client.get(reverse("audit:logs") + "?action=Reset+Password")
        assert resp_filter.status_code == 200
        assert b"Reset admin." in resp_filter.content
        assert b"Wiped product." not in resp_filter.content
