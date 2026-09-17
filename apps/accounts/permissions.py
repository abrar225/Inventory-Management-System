"""Role-to-permission matrix — the single source of truth for authorization.

Each role maps to a Django auth Group carrying a set of permissions. This
module declares, per role, which permissions the group should hold. The
``sync_roles`` management command reads this matrix and reconciles Group
membership, and is safe to re-run as later phases introduce new models and
their permissions.

Permissions are referenced as ``"<app_label>.<codename>"`` strings. Django
auto-creates ``add`` / ``change`` / ``delete`` / ``view`` permissions for every
model; custom permissions (declared in a model's ``Meta.permissions``) are
listed here as they are introduced.

Because business models arrive in later phases, some referenced permissions
may not exist yet. ``sync_roles`` skips unknown permissions with a warning
rather than failing, so the command stays runnable at every phase.
"""

from apps.accounts.models import Role

# Administrator always receives every permission, so it is handled specially
# in sync_roles rather than being enumerated here.
ADMINISTRATOR = Role.Name.ADMINISTRATOR
INVENTORY_MANAGER = Role.Name.INVENTORY_MANAGER
SALES_STAFF = Role.Name.SALES_STAFF

# Permissions granted to the Inventory Manager group.
# Can access: dashboard, products, categories, suppliers, purchases, sales,
# inventory, reports. Cannot: manage users, audit logs, or system settings.
INVENTORY_MANAGER_PERMS: list[str] = [
    # Catalog — full management
    "catalog.add_category",
    "catalog.change_category",
    "catalog.delete_category",
    "catalog.view_category",
    "catalog.add_supplier",
    "catalog.change_supplier",
    "catalog.delete_supplier",
    "catalog.view_supplier",
    "catalog.add_product",
    "catalog.change_product",
    "catalog.delete_product",
    "catalog.view_product",
    # Purchasing — full management
    "purchasing.add_purchase",
    "purchasing.change_purchase",
    "purchasing.view_purchase",
    "purchasing.view_purchaseitem",
    # Sales — full management
    "sales.add_sale",
    "sales.change_sale",
    "sales.view_sale",
    "sales.view_saleitem",
    # Inventory — manage stock and adjustments
    "inventory.view_stockmovement",
    "inventory.add_stockadjustment",
    "inventory.view_stockadjustment",
]

# Permissions granted to the Sales Staff group.
# Can access: dashboard, sales, products (view), inventory (read only),
# reports (sales only). Cannot: delete products, manage suppliers, manage
# purchases, or manage users.
SALES_STAFF_PERMS: list[str] = [
    # Catalog — read-only products & categories
    "catalog.view_product",
    "catalog.view_category",
    # Sales — create and view
    "sales.add_sale",
    "sales.change_sale",
    "sales.view_sale",
    "sales.view_saleitem",
    # Inventory — read only
    "inventory.view_stockmovement",
    "inventory.view_stockadjustment",
]

# The matrix consumed by sync_roles. Administrator is intentionally absent:
# it is granted all permissions programmatically.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    INVENTORY_MANAGER: INVENTORY_MANAGER_PERMS,
    SALES_STAFF: SALES_STAFF_PERMS,
}

# Human-readable descriptions seeded onto the Role rows.
ROLE_DESCRIPTIONS: dict[str, str] = {
    ADMINISTRATOR: "Full system access, including users and audit logs.",
    INVENTORY_MANAGER: (
        "Manages catalog, purchases, sales, and inventory. No user or audit "
        "administration."
    ),
    SALES_STAFF: (
        "Records sales and views products and inventory. Read-only reporting."
    ),
}
