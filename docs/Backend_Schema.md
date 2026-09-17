# BACKEND SCHEMA SPECIFICATION

## Inventory Management System (IMS)

Version: 1.0

Depends On

* PRD v1.0
* App Flow v1.0
* Tech Stack v1.0
* Frontend Guidelines v1.0

---

# 1. Architecture Overview

The backend follows Django's MVT architecture with a modular, domain-oriented structure.

```text
config/
│
├── accounts/
├── dashboard/
├── catalog/
│      ├── categories
│      ├── products
│      └── suppliers
│
├── purchasing/
├── sales/
├── inventory/
├── reporting/
├── audit/
└── common/
```

---

# 2. Database Principles

Every table must:

* Use UUID primary keys
* Include timestamps
* Use database constraints
* Support indexing
* Avoid duplicate data
* Preserve referential integrity

---

# 3. Base Model

Every model inherits from BaseModel.

```text
id UUID PK

created_at

updated_at

created_by

updated_by
```

---

# 4. User Entity

Table

```text
users
```

Columns

| Column     | Type     |
| ---------- | -------- |
| id         | UUID     |
| email      | Unique   |
| username   | Unique   |
| first_name | String   |
| last_name  | String   |
| password   | Hash     |
| phone      | String   |
| avatar     | Image    |
| role       | FK Role  |
| is_active  | Boolean  |
| last_login | DateTime |

Relationships

```text
Role

↓

User

↓

Purchases

Sales

Audit Logs
```

---

# 5. Role

```text
roles
```

Columns

```text
id

name

description
```

Three default roles

Administrator

Inventory Manager

Sales Staff

---

# 6. Category

```text
categories
```

Columns

```text
id

name

slug

description

status

created_at

updated_at
```

Relationship

```text
Category

↓

Products
```

One category

Many products

---

# 7. Supplier

```text
suppliers
```

Columns

```text
id

company_name

contact_person

email

phone

gst_number

address

city

state

postal_code

country

notes

status
```

Relationship

```text
Supplier

↓

Products

↓

Purchases
```

---

# 8. Product

Table

```text
products
```

Columns

```text
id

sku

barcode

name

slug

category_id

supplier_id

purchase_price

selling_price

minimum_stock

unit

description

image

is_active
```

Relationship

```text
Category

↓

Product

↓

Purchase Item

↓

Sale Item

↓

Stock Movement
```

Rules

SKU unique

Price validation

No duplicate barcode

---

# 9. Purchase

Table

```text
purchases
```

Columns

```text
id

purchase_number

supplier_id

purchase_date

subtotal

tax

discount

grand_total

status

notes

created_by
```

Relationship

```text
Supplier

↓

Purchase

↓

Purchase Items
```

---

# 10. Purchase Item

Table

```text
purchase_items
```

Columns

```text
id

purchase_id

product_id

quantity

unit_price

line_total
```

One purchase

Many items

---

# 11. Sale

Table

```text
sales
```

Columns

```text
id

invoice_number

customer_name

sale_date

subtotal

tax

discount

grand_total

status

created_by
```

Relationship

```text
Sale

↓

Sale Items
```

---

# 12. Sale Item

Table

```text
sale_items
```

Columns

```text
id

sale_id

product_id

quantity

unit_price

line_total
```

---

# 13. Stock Movement (Ledger)

Most important table.

```text
stock_movements
```

Columns

```text
id

product_id

movement_type

reference_type

reference_id

quantity

balance_after

reason

created_by

created_at
```

Movement Type

```text
PURCHASE

SALE

ADJUSTMENT
```

Reference Type

```text
Purchase

Sale

Adjustment
```

---

Relationship

```text
Product

↓

Stock Movement

↓

History
```

Every stock modification inserts one row.

Nothing edits history.

Ever.

---

# 14. Stock Adjustment

Table

```text
stock_adjustments
```

Columns

```text
id

product_id

adjustment_type

quantity

reason

approved_by

created_by

created_at
```

Adjustment Types

Increase

Decrease

Correction

Damage

Return

Lost

---

# 15. Audit Log

Table

```text
audit_logs
```

Columns

```text
id

user_id

action

model_name

object_id

ip_address

changes

created_at
```

Read only.

Never editable.

---

# 16. Dashboard View Model

No database table.

Generated dynamically.

Returns

```text
Products Count

Sales Count

Purchase Count

Inventory Value

Low Stock

Charts
```

---

# 17. Reports

No tables.

ORM aggregations.

---

# 18. Entity Relationship Diagram

```text
Role
 │
 │
 ▼
User
 │
 │
 ├──────────────┐
 │              │
 ▼              ▼
Purchase      Sale
 │              │
 ▼              ▼
PurchaseItem  SaleItem
       │         │
       └────┬────┘
            ▼
         Product
            │
     ┌──────┴────────┐
     ▼               ▼
 Category       Supplier
            │
            ▼
     StockMovement
            │
            ▼
    StockAdjustment

User
 │
 ▼
AuditLog
```

---

# 19. Authentication Flow

```text
Login

↓

Authenticate

↓

Session Created

↓

Permission Check

↓

Dashboard
```

---

Permission middleware executes before every protected view.

---

# 20. Product Creation Flow

```text
Open Form

↓

Validate

↓

Save Product

↓

Commit Transaction

↓

Redirect
```

---

# 21. Purchase Transaction

```text
Create Purchase

↓

Save Purchase

↓

Save Items

↓

Increase Stock

↓

Insert Ledger

↓

Commit
```

Entire operation

Single database transaction.

---

# 22. Sale Transaction

```text
Create Sale

↓

Check Stock

↓

Save Sale

↓

Save Items

↓

Decrease Stock

↓

Ledger Entry

↓

Commit
```

If stock insufficient

Rollback everything.

---

# 23. Stock Adjustment Flow

```text
Adjustment Form

↓

Reason Required

↓

Approval

↓

Ledger Entry

↓

Update Current Stock

↓

Commit
```

---

# 24. Inventory Calculation

Current Stock

```text
Purchases

+

Adjustments

-

Sales
```

Never manually edited.

---

# 25. Soft Delete Policy

Allowed

Products

Suppliers

Categories

Users

Not Allowed

Purchases

Sales

Ledger

Audit Logs

Historical records remain immutable.

---

# 26. Database Indexes

Create indexes on

```text
SKU

Barcode

Email

Purchase Number

Invoice Number

Category

Supplier

Created Date

Movement Date

Product Name
```

Composite indexes

```text
Category + Status

Supplier + Status

Movement Type + Date

Sale Date + Status

Purchase Date + Status
```

---

# 27. Constraints

Unique

```text
SKU

Barcode

Category Name

Role Name

Purchase Number

Invoice Number
```

Check Constraints

Selling Price ≥ Purchase Price

Quantity > 0

Stock ≥ 0

Tax ≥ 0

Discount ≥ 0

---

# 28. Transactions

Must be atomic

Purchase

Sale

Stock Adjustment

User Creation

Role Assignment

Never partially save.

---

# 29. Validation Rules

Product

SKU unique

Price valid

Category required

Supplier required

---

Purchase

Supplier required

One item minimum

Positive quantity

---

Sale

Stock available

Positive quantity

---

Supplier

Unique email

Valid phone

---

Category

Unique name

---

# 30. Business Rules

Cannot sell unavailable stock.

Cannot delete supplier with products.

Cannot delete category with products.

Cannot delete role assigned to users.

Cannot reduce stock below zero.

Cannot edit completed sales.

Cannot edit completed purchases.

Ledger immutable.

Audit immutable.

---

# 31. Services Layer

Business logic must not live in views.

Create service modules.

```text
ProductService

PurchaseService

SaleService

InventoryService

ReportingService

UserService

AuditService
```

Views call services.

Services access models.

---

# 32. Signals

Use Django signals sparingly.

Allowed

Create Audit Log

Update timestamps

Invalidate cache (future)

Not allowed

Stock calculations

Financial calculations

Business workflows

Critical inventory logic should remain explicit in service methods and transactions.

---

# 33. Repository Pattern

Do **not** implement a repository pattern.

Use Django ORM directly.

Encapsulate complex queries in:

* Custom QuerySets
* Model Managers
* Service layer

---

# 34. Error Handling

Raise domain-specific exceptions:

```text
InsufficientStockError

DuplicateSKUError

InvalidPriceError

PermissionDeniedError

InactiveUserError

InvalidPurchaseError

InvalidSaleError
```

Views translate exceptions into user-facing responses.

---

# 35. Concurrency Control

Inventory operations must be safe under concurrent requests.

Requirements:

* Wrap purchases, sales, and adjustments in `transaction.atomic()`.
* Lock affected product rows using `select_for_update()`.
* Prevent race conditions that could oversell stock.
* Never rely on client-side validation for stock availability.

---

# 36. Query Optimization

Always:

* Use `select_related()` for ForeignKey relationships.
* Use `prefetch_related()` for reverse relationships.
* Paginate large lists.
* Avoid N+1 queries.
* Add indexes before introducing caching.

---

# 37. File Storage

Product images

```text
/media/products/
```

User avatars

```text
/media/users/
```

Use unique filenames.

Validate MIME type and file size.

---

# 38. State Machines

Purchase Status:

```text
Draft
↓
Completed
↓
Cancelled
```

Sale Status:

```text
Draft
↓
Completed
↓
Cancelled
```

Only **Completed** purchases or sales affect inventory.

Draft records are editable.

Completed records become read-only.

Cancelled records preserve history but do not alter stock further.

---

# 39. Current Stock Strategy

For performance and correctness:

* `Product.current_stock` stores the current quantity.
* `StockMovement` is the immutable audit ledger.
* Every stock-changing transaction:

  1. Locks the product row.
  2. Updates `current_stock`.
  3. Creates a `StockMovement` record.
  4. Commits atomically.

Periodic reconciliation can verify that `current_stock` matches the ledger totals.

This avoids expensive ledger summation on every page load while preserving complete history.

---

# 40. Backend Quality Checklist

The backend is considered complete only if:

* Every table uses UUID primary keys.
* Every critical write operation is atomic.
* Stock cannot become negative.
* All inventory changes are recorded in `StockMovement`.
* Completed purchases and sales are immutable.
* Soft deletion is applied only where specified.
* Foreign keys enforce referential integrity.
* Validation exists at the model, form, and service layers where appropriate.
* Permission checks exist on every protected endpoint.
* Audit logs are immutable.
* ORM queries are optimized.
* Critical business rules are covered by automated tests.
* The schema is normalized (3NF where practical) and avoids unnecessary duplication.

---

## One improvement before Document 6 (Implementation Plan)

I would add one more architectural layer that many AI coding agents struggle to invent consistently:

**Define explicit domain services before writing any views.**

For example:

* `PurchaseService.complete_purchase()`
* `SaleService.complete_sale()`
* `InventoryService.adjust_stock()`
* `InventoryService.reconcile_stock()`
* `ProductService.create_product()`


