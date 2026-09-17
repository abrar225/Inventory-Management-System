# APP FLOW DOCUMENT

## Inventory Management System (IMS)

Version: 1.0

Depends on: PRD v1.0

---

# 1. Application Structure

The application follows a dashboard-first architecture.

```
Authentication

        │

        ▼

Dashboard

 ├── Products
 ├── Categories
 ├── Suppliers
 ├── Purchases
 ├── Sales
 ├── Inventory
 ├── Reports
 ├── Users (Admin)
 ├── Audit Logs (Admin)
 └── Profile
```

Users never access internal pages before authentication.

---

# 2. High-Level Navigation

```
Login

↓

Dashboard

↓

Sidebar Navigation

├ Dashboard
├ Products
├ Categories
├ Suppliers
├ Purchases
├ Sales
├ Inventory
├ Reports
├ User Management
├ Audit Logs
├ Profile
└ Logout
```

The sidebar remains visible throughout the authenticated experience.

The header remains fixed.

---

# 3. Authentication Flow

## User visits application

↓

```
/
```

↓

Redirect

```
/login
```

---

## Login Page

User enters

* Email
* Password

↓

Validation

If invalid

↓

Display inline errors

↓

Stay on Login

---

If valid

↓

Check account status

If inactive

↓

Show

```
Account Disabled
```

Remain on Login

---

If active

↓

Create session

↓

Redirect

```
Dashboard
```

---

Logout

↓

Destroy session

↓

Redirect Login

---

Forgot Password

↓

Enter Email

↓

Receive reset link

↓

Reset Password

↓

Login

---

# 4. Dashboard Flow

Dashboard is always the landing page after login.

Displays

```
Summary Cards

↓

Charts

↓

Low Stock Widget

↓

Recent Purchases

↓

Recent Sales

↓

Quick Actions
```

Quick Actions

```
Add Product

New Purchase

New Sale

Add Supplier
```

Clicking any card navigates to its module.

Example

```
Total Products

↓

Products List
```

---

# 5. Global Layout

Every authenticated page contains

```
Header

Sidebar

Breadcrumb

Page Title

Actions

Content

Footer
```

---

Header

Contains

```
Search

Notifications

Profile Menu
```

---

Sidebar

Contains

```
Dashboard

Products

Categories

Suppliers

Purchases

Sales

Inventory

Reports

Users

Audit Logs

Profile

Logout
```

---

# 6. Products Flow

Products

↓

Products List

Displays

```
Search

Filters

Table

Pagination

Create Button
```

---

User clicks

```
Create Product
```

↓

Product Form

↓

Fill Information

↓

Save

↓

Validation

If invalid

↓

Show field errors

Stay on form

---

If valid

↓

Save Database

↓

Success Message

↓

Redirect

Products List

---

Click Product Row

↓

Product Detail

Contains

```
Information

Stock

Supplier

Category

History

Actions
```

Actions

```
Edit

Delete
```

---

Edit

↓

Product Form

↓

Save

↓

Redirect Detail

---

Delete

↓

Confirmation Modal

↓

Cancel

Return

OR

Confirm

↓

Soft Delete

↓

Success

↓

Products List

---

# 7. Categories Flow

Categories

↓

Categories List

↓

Search

↓

Create Category

↓

Save

↓

Redirect List

---

Selecting Category

↓

Category Detail

↓

Edit

↓

Save

↓

Return

---

Delete

↓

Confirmation

↓

Remove if unused

Otherwise

Show

```
Category in use
```

Cannot delete.

---

# 8. Supplier Flow

Suppliers

↓

Supplier List

↓

Supplier Detail

Shows

```
Information

Products

Purchase History
```

---

Edit

↓

Update

↓

Return

---

Delete

↓

Allowed only when supplier has no linked products.

Otherwise

Display warning.

---

# 9. Purchase Flow

Purchases

↓

Purchase List

↓

New Purchase

↓

Select Supplier

↓

Add Products

↓

Enter Quantity

↓

Enter Cost

↓

Review

↓

Save Purchase

↓

Transaction

↓

Increase Stock

↓

Create Stock Movement

↓

Success

↓

Purchase Detail

---

Purchase Detail

Contains

```
Invoice

Supplier

Products

Totals

Print
```

---

# 10. Sales Flow

Sales

↓

Sales List

↓

New Sale

↓

Select Products

↓

Check Stock

↓

Enter Quantity

↓

Totals Calculate

↓

Save Sale

↓

Transaction

↓

Reduce Stock

↓

Create Stock Movement

↓

Success

↓

Invoice Detail

---

If requested quantity exceeds stock

↓

Show

```
Insufficient Inventory
```

Remain on page.

---

# 11. Inventory Flow

Inventory

↓

Inventory Dashboard

Contains

```
Current Stock

Low Stock

Out of Stock

Stock Value
```

---

Select Product

↓

Inventory Detail

Shows

```
Current Quantity

History

Adjustments

Movement Timeline
```

---

Stock Adjustment

↓

Reason Required

↓

Update

↓

Log Adjustment

↓

Success

---

# 12. Reports Flow

Reports

↓

Report Dashboard

Contains

```
Sales

Purchases

Inventory

Products

Suppliers
```

---

Choose Report

↓

Date Filter

↓

Generate

↓

Display Table

↓

Export

```
CSV

Excel

Print
```

---

# 13. User Management Flow

Admin Only

↓

Users List

↓

Create User

↓

Assign Role

↓

Save

↓

Email Invitation (future)

---

Selecting User

↓

Profile

↓

Reset Password

↓

Deactivate

↓

Change Role

---

Inactive users

Cannot Login.

---

# 14. Audit Log Flow

Admin Only

↓

Audit Logs

↓

Filter

↓

Search

↓

View Details

No Editing

No Deleting

Read Only

---

# 15. Profile Flow

Profile

↓

View Information

↓

Edit

↓

Upload Avatar

↓

Change Password

↓

Save

---

# 16. Global Search Flow

Search box

↓

User types

↓

Search executes

↓

Results

```
Products

Categories

Suppliers

Purchases

Sales
```

Click Result

↓

Navigate directly

---

# 17. Breadcrumb Navigation

Example

```
Dashboard

↓

Products

↓

Product Detail

↓

Edit
```

Displayed as

```
Dashboard

>

Products

>

iPhone 16

>

Edit
```

---

# 18. Permission Flow

## Administrator

Can access

Everything.

---

Inventory Manager

Can access

Dashboard

Products

Categories

Suppliers

Purchases

Sales

Inventory

Reports

Cannot access

Users

Audit Logs

System Settings

---

Sales Staff

Can access

Dashboard

Sales

Products

Inventory (Read Only)

Reports (Sales Only)

Cannot

Delete Products

Manage Suppliers

Manage Purchases

Manage Users

---

# 19. Empty States

Products

```
No products found.

Create your first product.
```

---

Suppliers

```
No suppliers available.
```

---

Sales

```
No sales recorded.
```

---

Purchases

```
No purchases recorded.
```

---

Inventory

```
Inventory is empty.
```

---

Reports

```
No data available for selected filters.
```

---

# 20. Confirmation Dialogs

Always required for

Delete Product

Delete Category

Delete Supplier

Delete User

Deactivate User

Logout

Reset Password

Stock Adjustment

---

# 21. Toast Notifications

Success

```
Product created successfully.
```

```
Purchase recorded successfully.
```

```
Sale completed successfully.
```

```
Supplier updated.
```

---

Error

```
Something went wrong.
```

```
Validation failed.
```

```
Permission denied.
```

```
Stock unavailable.
```

---

Warning

```
Low stock detected.
```

```
Category already exists.
```

---

# 22. Error Handling Flow

Validation Error

↓

Stay on Page

↓

Highlight Invalid Fields

↓

Display Messages

---

Permission Error

↓

403 Page

↓

Return Dashboard

---

Not Found

↓

404 Page

↓

Back to Dashboard

---

Server Error

↓

500 Page

↓

Retry Button

↓

Contact Administrator

---

# 23. Complete User Journey

```text
Open Application
        │
        ▼
Login
        │
        ▼
Dashboard
        │
        ├──────────────► Products
        │                     │
        │                     ▼
        │              Create Product
        │                     │
        │                     ▼
        │              Save Successfully
        │                     │
        │                     ▼
        │              Product Detail
        │
        ├──────────────► Suppliers
        │                     │
        │                     ▼
        │             Create Supplier
        │
        ├──────────────► Purchases
        │                     │
        │                     ▼
        │              Record Purchase
        │                     │
        │                     ▼
        │             Stock Increases
        │
        ├──────────────► Sales
        │                     │
        │                     ▼
        │               Record Sale
        │                     │
        │                     ▼
        │             Stock Decreases
        │
        ├──────────────► Inventory
        │                     │
        │                     ▼
        │              View Movements
        │
        ├──────────────► Reports
        │                     │
        │                     ▼
        │             Export Report
        │
        ├──────────────► Profile
        │
        ▼
Logout
```

---

## One architectural improvement before moving on

There's one change I'd make to the PRD and App Flow because it reflects how real inventory systems operate.

Instead of keeping **Inventory** as a CRUD module, treat it as a **read-only stock ledger**. Users should **never directly edit stock quantities** except through a controlled **Stock Adjustment** operation. Inventory changes should come only from:

* Purchases → stock increases
* Sales → stock decreases
* Stock Adjustments → manual corrections with a mandatory reason


