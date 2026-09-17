# IMPLEMENTATION PLAN

## Inventory Management System (IMS)

Version: 1.0

Depends On

* PRD v1.0
* App Flow v1.0
* Tech Stack v1.0
* Frontend Guidelines v1.0
* Backend Schema v1.0

---

# 1. Development Principles

The AI coding agent **must** follow these rules throughout development:

* Build incrementally.
* Never implement unfinished features.
* Complete one phase before starting the next.
* Keep the application runnable after every phase.
* Write tests for critical business logic as each feature is added.
* Refactor immediately when duplication appears.
* Do not skip migrations.
* Do not generate placeholder code.
* Do not leave TODOs in production code.

---

# 2. Overall Build Order

```text
Phase 1  → Project Foundation

Phase 2  → Authentication & Roles

Phase 3  → Design System

Phase 4  → Core Catalog

Phase 5  → Inventory Domain

Phase 6  → Purchasing

Phase 7  → Sales

Phase 8  → Dashboard

Phase 9  → Reporting

Phase 10 → Audit & Logging

Phase 11 → Testing

Phase 12 → Optimization

Phase 13 → Production Readiness
```

Each phase is considered complete only after:

* application runs
* migrations succeed
* tests pass
* UI is functional
* no console errors
* no linting errors

---

# PHASE 1

## Project Foundation

### Objectives

Create a production-ready Django project structure.

---

Tasks

* Create Django project
* Configure settings split (`base.py`, `dev.py`, `prod.py`)
* Configure PostgreSQL
* Configure Tailwind CSS
* Configure HTMX
* Configure Alpine.js
* Configure WhiteNoise
* Configure media/static
* Configure environment variables
* Configure logging
* Configure URL routing
* Create reusable `BaseModel`
* Configure UUID primary keys
* Configure global templates
* Configure base layout
* Configure error pages (403, 404, 500)

Deliverables

* Project starts successfully
* Database connection works
* Static files work
* Tailwind builds correctly
* Base layout renders

---

# PHASE 2

## Authentication & Authorization

Modules

accounts

Objectives

Implement secure authentication.

Tasks

* Custom User model
* Role model
* Django Groups
* Login
* Logout
* Password reset
* Profile page
* Avatar upload
* Permission decorators
* Middleware
* Session management

Tests

Authentication

Permissions

Inactive user login

Password reset

Deliverables

Users can securely log in and role permissions work.

---

# PHASE 3

## Design System

Modules

common

Objectives

Build every reusable UI component before any business pages.

Components

* Button
* Card
* Modal
* Table
* Badge
* Input
* Select
* Textarea
* Toast
* Alert
* Pagination
* Breadcrumb
* Empty State
* Skeleton Loader
* KPI Card
* Dropdown
* Search Bar
* File Upload
* Avatar

Deliverables

Complete reusable component library.

No duplicated HTML patterns.

---

# PHASE 4

## Catalog Domain

Modules

categories

suppliers

products

Objectives

Implement the product catalog.

Sequence

### Categories

* Model
* Migration
* Forms
* Service
* Views
* Templates
* Tests

---

### Suppliers

Same order.

---

### Products

Model

Validation

Image upload

CRUD

Search

Filters

Pagination

Soft delete

Product detail

Tests

Deliverables

Complete catalog management.

---

# PHASE 5

## Inventory Domain

Modules

inventory

Objectives

Build stock management before purchases and sales.

Models

StockMovement

StockAdjustment

Services

InventoryService

Functions

Adjust stock

Reconcile stock

Stock history

Current stock

Low stock

Views

Inventory dashboard

Movement history

Adjustment form

Tests

Ledger integrity

Stock calculations

Negative stock prevention

Deliverables

Inventory engine complete.

---

# PHASE 6

## Purchasing Domain

Modules

purchasing

Objectives

Increase inventory through purchases.

Sequence

Purchase model

PurchaseItem model

Forms

Services

Views

Templates

Printing

Validation

Atomic transactions

Ledger updates

Tests

Rollback

Stock increase

Totals

Deliverables

Purchases correctly update inventory.

---

# PHASE 7

## Sales Domain

Modules

sales

Objectives

Decrease inventory.

Sequence

Sale model

SaleItem

Invoice

Services

Validation

Templates

Transactions

Inventory deduction

Ledger

Tests

Insufficient stock

Rollback

Totals

Deliverables

Sales complete.

---

# PHASE 8

## Dashboard

Modules

dashboard

Widgets

KPI cards

Charts

Recent sales

Recent purchases

Low stock

Inventory value

Top products

Quick actions

Charts

Sales trend

Purchase trend

Category distribution

Deliverables

Fully functional dashboard.

---

# PHASE 9

## Reporting

Modules

reporting

Reports

Sales

Purchases

Inventory

Products

Suppliers

Exports

CSV

Excel

PDF

Print

Filters

Date range

Category

Supplier

Deliverables

All reports export correctly.

---

# PHASE 10

## Audit & Logging

Modules

audit

Objectives

Track every important action.

Audit

Login

Logout

Create

Update

Delete

Stock changes

Permission changes

Views

Read-only

Search

Filters

Deliverables

Immutable audit system.

---

# PHASE 11

## Testing

Coverage Target

85%+

Model Tests

View Tests

Form Tests

Service Tests

Permission Tests

Integration Tests

Regression Tests

Critical Rules

No negative stock

Ledger integrity

Role permissions

Atomic transactions

Deliverables

Reliable codebase.

---

# PHASE 12

## Performance Optimization

Tasks

Database indexes

select_related()

prefetch_related()

Pagination

Image optimization

Query optimization

Template optimization

Static compression

Deliverables

Fast application.

---

# PHASE 13

## Production Readiness

Tasks

DEBUG=False

Security headers

Secure cookies

CSRF

Environment validation

Collectstatic

Logging

Backup strategy

Health check

README

Deployment guide

Deliverables

Production-ready application.

---

# 3. Internal Build Order Within Each Module

Every module follows the same sequence.

```text
Requirements

↓

Models

↓

Migrations

↓

Admin

↓

Forms

↓

Validators

↓

Services

↓

QuerySets

↓

Views

↓

URLs

↓

Templates

↓

Components

↓

Permissions

↓

Tests

↓

Documentation
```

Never change this order.

---

# 4. Git Milestones

Commit after every completed step.

Example

```text
feat(accounts): implement custom user model

feat(products): add product CRUD

feat(inventory): implement stock ledger

feat(sales): complete invoice workflow

fix(inventory): prevent negative stock
```

No large "miscellaneous" commits.

---

# 5. Testing Gates

A phase cannot proceed unless:

* All migrations apply cleanly.
* Unit tests pass.
* No failing lint rules.
* Type checking passes.
* Manual smoke test succeeds.
* UI matches the design system.

---

# 6. AI Coding Rules

The AI coding agent **must not**:

* Skip validations.
* Skip transactions.
* Duplicate business logic.
* Write SQL when ORM suffices.
* Hardcode permissions.
* Hardcode URLs.
* Use inline CSS.
* Introduce unused dependencies.
* Mix business logic into templates.
* Store inventory logic in signals.

---

# 7. Definition of Done (Per Feature)

A feature is complete only if it includes:

* Database model
* Migration
* Admin configuration
* Forms
* Validation
* Service methods
* Views
* URLs
* Templates
* Permission checks
* Automated tests
* Documentation (docstrings where appropriate)

---

# 8. Risk Management

Potential Risks

* Race conditions during concurrent sales
* Duplicate SKU creation
* Inconsistent stock updates
* Broken permission inheritance
* N+1 ORM queries
* Large report generation time
* Image upload failures

Mitigations

* `transaction.atomic()`
* `select_for_update()`
* Database unique constraints
* Service-layer business rules
* Optimized ORM queries
* Pagination and streaming exports
* File validation and size limits

---

# 9. Performance Targets

* Initial page load: **< 2 seconds**
* Dashboard render: **< 3 seconds**
* Search response: **< 500 ms**
* CRUD operations: **< 300 ms**
* Report generation (1,000 records): **< 5 seconds**
* Support at least **100 concurrent users**
* Support **10,000+ products**

---

# 10. Final Acceptance Checklist

The project is considered complete only when:

### Functional

* All PRD requirements are implemented.
* App Flow matches the documented behavior.
* Role-based permissions work correctly.
* Inventory calculations are accurate.
* Purchases increase stock.
* Sales decrease stock.
* Stock adjustments are audited.
* Reports export correctly.

### Technical

* PostgreSQL schema matches the Backend Schema document.
* All critical operations use transactions.
* UUID primary keys are used consistently.
* No duplicated business logic.
* Reusable UI components are used throughout.

### Quality

* Test coverage ≥ 85%.
* No critical security issues.
* No linting or formatting errors.
* Responsive on desktop, tablet, and mobile.
* Accessible (WCAG-oriented practices).
* Production configuration validated.

---

# 11. AI Execution Strategy (Mandatory)

The AI coding agent should execute the project in this loop for **every phase**:

```text
Read documentation
        ↓
Design models/services
        ↓
Implement feature
        ↓
Run migrations
        ↓
Run tests
        ↓
Fix failures
        ↓
Optimize code
        ↓
Verify UI
        ↓
Commit changes
        ↓
Proceed to next phase
```

The agent **must never start a new phase if the current one is incomplete or failing**.

---

# 12. Repository Deliverables

By the end of the project, the repository should include:

```text
README.md
CHANGELOG.md
LICENSE
.env.example
requirements.txt
pyproject.toml
.pre-commit-config.yaml
ruff.toml
mypy.ini

/docs/
    PRD.md
    App_Flow.md
    Tech_Stack.md
    Frontend_Guidelines.md
    Backend_Schema.md
    Implementation_Plan.md
    API_Notes.md (future)

/config/
/apps/
/templates/
/static/
/media/
/tests/
```

---

# Final Recommendation: Add a "Project Constitution"

If I were building this with Claude Code Opus 4.8, I would add **one more document before writing a single line of code**:

> **Project Constitution (`CONSTITUTION.md`)**

This isn't another requirements document. It's a **non-negotiable engineering rulebook** that every prompt reminds the coding agent to follow.

Examples of rules:

* Never violate the PRD without explicit approval.
* Never introduce a new dependency without justification.
* Never bypass service-layer business logic.
* Never duplicate UI components.
* Never write business logic in templates.
* Never skip tests for inventory-changing operations.
* Never merge code that fails linting or type checking.
* Prefer readability over cleverness.
* Preserve backward compatibility within the project.
* Keep every commit in a runnable state.

