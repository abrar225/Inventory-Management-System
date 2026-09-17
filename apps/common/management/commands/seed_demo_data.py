from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.accounts.services import UserService
from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockAdjustment
from apps.inventory.services import InventoryService
from apps.purchasing.models import Purchase
from apps.purchasing.services import PurchasingService
from apps.sales.services import SalesService


class Command(BaseCommand):
    """Seed the database with a high-fidelity demonstration dataset."""

    help = "Populate database with demo users, catalog, stock ledger, purchases, and sales."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Initializing system demo data seeding...")

        # 1. Run role synchronization to guarantee Role-to-Group mappings exist
        self.stdout.write("Synchronizing roles and Django groups...")
        call_command("sync_roles")

        admin_role = Role.objects.get(name=Role.Name.ADMINISTRATOR)
        manager_role = Role.objects.get(name=Role.Name.INVENTORY_MANAGER)
        staff_role = Role.objects.get(name=Role.Name.SALES_STAFF)

        # 2. Create users
        self.stdout.write("Seeding user accounts...")
        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "username": "admin",
                "first_name": "College",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("password123!")
            admin_user.save()
            UserService.assign_role(admin_user, admin_role)
            self.stdout.write("Created admin@example.com (pw: password123!)")
        else:
            admin_user = User.objects.get(email="admin@example.com")

        manager_user, created = User.objects.get_or_create(
            email="manager@example.com",
            defaults={
                "username": "manager",
                "first_name": "Stock",
                "last_name": "Manager",
                "is_staff": True,
            },
        )
        if created:
            manager_user.set_password("password123!")
            manager_user.save()
            UserService.assign_role(manager_user, manager_role)
            self.stdout.write("Created manager@example.com (pw: password123!)")
        else:
            manager_user = User.objects.get(email="manager@example.com")

        staff_user, created = User.objects.get_or_create(
            email="staff@example.com",
            defaults={
                "username": "staff",
                "first_name": "Sales",
                "last_name": "Staff",
                "is_staff": False,
            },
        )
        if created:
            staff_user.set_password("password123!")
            staff_user.save()
            UserService.assign_role(staff_user, staff_role)
            self.stdout.write("Created staff@example.com (pw: password123!)")
        else:
            staff_user = User.objects.get(email="staff@example.com")

        # 3. Create Categories
        self.stdout.write("Seeding categories...")
        electronics, _ = Category.objects.get_or_create(
            name="Electronics",
            defaults={"description": "Devices, components, and electronic accessories."},
        )
        stationery, _ = Category.objects.get_or_create(
            name="Stationery",
            defaults={"description": "Office paper, pens, and desk organization items."},
        )
        wearables, _ = Category.objects.get_or_create(
            name="Wearables",
            defaults={"description": "Fitness trackers, watches, and smart gear."},
        )

        # 4. Create Suppliers
        self.stdout.write("Seeding suppliers...")
        tech_supplier, _ = Supplier.objects.get_or_create(
            company_name="Apex Tech Solutions",
            defaults={
                "contact_person": "Vikram Sen",
                "email": "contact@apextech.com",
                "phone": "+919876543201",
                "address": "102 Tech Park, Phase 1",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India",
            },
        )
        stationery_supplier, _ = Supplier.objects.get_or_create(
            company_name="Global Office Supplies",
            defaults={
                "contact_person": "Meera Joshi",
                "email": "sales@globaloffice.com",
                "phone": "+919876543202",
                "address": "45 Stationery Lane",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postal_code": "400001",
                "country": "India",
            },
        )

        # 5. Create Products
        self.stdout.write("Seeding products catalog...")
        products_data = [
            # Electronics
            {
                "name": "MacBook Pro 14",
                "sku": "MAC14PRO",
                "category": electronics,
                "supplier": tech_supplier,
                "purchase_price": Decimal("120000.00"),
                "selling_price": Decimal("145000.00"),
                "current_stock": 15,
                "minimum_stock": 3,
                "unit": "PCS",
            },
            {
                "name": "Sony WH-1000XM5",
                "sku": "SONYXM5",
                "category": electronics,
                "supplier": tech_supplier,
                "purchase_price": Decimal("22000.00"),
                "selling_price": Decimal("29999.00"),
                "current_stock": 25,
                "minimum_stock": 5,
                "unit": "PCS",
            },
            {
                "name": "Samsung T7 1TB SSD",
                "sku": "SAMT71TB",
                "category": electronics,
                "supplier": tech_supplier,
                "purchase_price": Decimal("7500.00"),
                "selling_price": Decimal("9999.00"),
                "current_stock": 8,  # low stock warning trigger
                "minimum_stock": 10,
                "unit": "PCS",
            },
            {
                "name": "Logitech MX Master 3S",
                "sku": "LOGIMX3S",
                "category": electronics,
                "supplier": tech_supplier,
                "purchase_price": Decimal("6500.00"),
                "selling_price": Decimal("8999.00"),
                "current_stock": 40,
                "minimum_stock": 8,
                "unit": "PCS",
            },
            # Stationery
            {
                "name": "Premium Notebook Moleskine",
                "sku": "NOTE-MB",
                "category": stationery,
                "supplier": stationery_supplier,
                "purchase_price": Decimal("120.00"),
                "selling_price": Decimal("249.00"),
                "current_stock": 150,
                "minimum_stock": 20,
                "unit": "PCS",
            },
            {
                "name": "Pilot Gel Pens Box of 12",
                "sku": "PENS-PILOT",
                "category": stationery,
                "supplier": stationery_supplier,
                "purchase_price": Decimal("400.00"),
                "selling_price": Decimal("600.00"),
                "current_stock": 12,  # low stock warning trigger
                "minimum_stock": 30,
                "unit": "BOXES",
            },
            # Wearables
            {
                "name": "Apple Watch Series 9",
                "sku": "APWTCH9",
                "category": wearables,
                "supplier": tech_supplier,
                "purchase_price": Decimal("32000.00"),
                "selling_price": Decimal("41900.00"),
                "current_stock": 1,  # critically low stock warning
                "minimum_stock": 5,
                "unit": "PCS",
            },
            {
                "name": "Fitbit Charge 6",
                "sku": "FITBITC6",
                "category": wearables,
                "supplier": tech_supplier,
                "purchase_price": Decimal("11000.00"),
                "selling_price": Decimal("14999.00"),
                "current_stock": 0,  # out of stock warning
                "minimum_stock": 5,
                "unit": "PCS",
            },
        ]

        products = []
        for p_info in products_data:
            prod, created = Product.objects.get_or_create(
                sku=p_info["sku"],
                defaults=p_info,
            )
            if created:
                self.stdout.write(f"Added product: {prod.name}")
            products.append(prod)

        # 6. Manual Stock Adjustments
        self.stdout.write("Seeding manual stock adjustments...")
        # Increase MX Master stock
        mx_mouse = Product.objects.get(sku="LOGIMX3S")
        if not StockAdjustment.objects.filter(product=mx_mouse).exists():
            InventoryService.adjust_stock(
                product=mx_mouse,
                quantity=10,
                adjustment_type=StockAdjustment.AdjustmentType.INCREASE,
                reason="Initial inventory count override.",
                created_by=admin_user,
            )

        # Decrease Sony headphones (lost in transit)
        sony = Product.objects.get(sku="SONYXM5")
        if not StockAdjustment.objects.filter(product=sony).exists():
            InventoryService.adjust_stock(
                product=sony,
                quantity=2,
                adjustment_type=StockAdjustment.AdjustmentType.LOST,
                reason="Damaged box/discarded item.",
                created_by=manager_user,
            )

        # 7. Purchase Orders (Draft, Ordered, Received)
        self.stdout.write("Seeding purchase order logs...")
        if not Purchase.objects.exists():
            # A received PO
            po_received = Purchase.objects.create(
                supplier=tech_supplier,
                purchase_number="PO-2026-0001",
                status=Purchase.Status.DRAFT,
                purchase_date=timezone.now().date() - timedelta(days=15),
                created_by=manager_user,
            )
            po_received.items.create(product=mx_mouse, quantity=20, unit_price=Decimal("6500.00"))
            po_received.status = Purchase.Status.ORDERED
            po_received.save()
            PurchasingService.receive_purchase(po_received, user=manager_user)

            # An ordered PO (pending arrival)
            po_pending = Purchase.objects.create(
                supplier=tech_supplier,
                purchase_number="PO-2026-0002",
                status=Purchase.Status.DRAFT,
                purchase_date=timezone.now().date() - timedelta(days=2),
                created_by=manager_user,
            )
            po_pending.items.create(product=sony, quantity=10, unit_price=Decimal("22000.00"))
            po_pending.status = Purchase.Status.ORDERED
            po_pending.save()

            # A draft PO
            po_draft = Purchase.objects.create(
                supplier=stationery_supplier,
                purchase_number="PO-2026-0003",
                status=Purchase.Status.DRAFT,
                purchase_date=timezone.now().date(),
                created_by=manager_user,
            )
            notebooks = Product.objects.get(sku="NOTE-MB")
            po_draft.items.create(product=notebooks, quantity=100, unit_price=Decimal("120.00"))

        # 8. Sales Invoices
        self.stdout.write("Seeding sales invoice logs...")
        from apps.sales.models import Sale
        if not Sale.objects.exists():
            # Invoice 1
            items1 = [
                {"product": mx_mouse, "quantity": 2, "unit_price": Decimal("8999.00")},
                {"product": sony, "quantity": 1, "unit_price": Decimal("29999.00")},
            ]
            SalesService.create_sale(
                customer_name="Aman Verma",
                sale_date=timezone.now().date() - timedelta(days=5),
                items_data=items1,
                tax=Decimal("1200.00"),
                discount=Decimal("500.00"),
                user=staff_user,
            )

            # Invoice 2
            items2 = [
                {"product": Product.objects.get(sku="NOTE-MB"), "quantity": 10, "unit_price": Decimal("249.00")},
            ]
            SalesService.create_sale(
                customer_name="XYZ University Library",
                sale_date=timezone.now().date(),
                items_data=items2,
                tax=Decimal("0.00"),
                discount=Decimal("100.00"),
                user=staff_user,
            )

        self.stdout.write(self.style.SUCCESS("Demo seeding completed successfully!"))
