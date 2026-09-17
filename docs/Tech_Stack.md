# TECH STACK SPECIFICATION

## Inventory Management System (IMS)

Version: 1.0

Depends On:

* PRD v1.0
* App Flow v1.0

---

# 1. Technology Philosophy

The application must follow these engineering principles:

* Server-side rendered architecture
* Django-first development
* Minimal JavaScript
* Production-grade project structure
* Security-first implementation
* Modular architecture
* High maintainability
* Scalable codebase
* Enterprise coding standards
* No unnecessary dependencies

---

# 2. Core Technology Stack

| Layer               | Technology       | Version  | Purpose                      |
| ------------------- | ---------------- | -------- | ---------------------------- |
| Language            | Python           | 3.13.x   | Backend language             |
| Framework           | Django           | 5.2 LTS  | Web framework                |
| Database            | PostgreSQL       | 17.x     | Primary relational database  |
| ORM                 | Django ORM       | Built-in | Database access              |
| Template Engine     | Django Templates | Built-in | Server-side rendering        |
| CSS                 | Tailwind CSS     | 4.x      | Styling system               |
| JavaScript          | Vanilla ES2023   | Native   | Client-side interactions     |
| Package Manager     | pip              | Latest   | Python dependency management |
| Virtual Environment | venv             | Built-in | Environment isolation        |

---

# 3. Backend Packages

## Django

Version

```text
5.2 LTS
```

Purpose

* Authentication
* ORM
* Admin
* Routing
* Forms
* Sessions
* Security
* Template Engine
* Middleware

---

## psycopg

Version

```text
3.x
```

Purpose

PostgreSQL database adapter.

---

## Pillow

Purpose

Image upload

Product images

Profile avatars

---

## django-environ

Purpose

Environment variables

Secrets

Configuration

---

## WhiteNoise

Purpose

Static file serving

Production deployment

---

## openpyxl

Purpose

Excel exports

Inventory reports

Sales reports

Purchases reports

---

## ReportLab

Purpose

PDF generation

Invoices

Reports

Print documents

---

## django-filter

Purpose

Advanced filtering

Search pages

Reports

---

## python-slugify

Purpose

Slug generation

Readable URLs

---

## django-import-export

Purpose

Bulk import/export

CSV

Excel

---

## Faker

Development only

Generate test data

---

## factory-boy

Development only

Factories

Testing

---

## pytest

Testing framework

---

## pytest-django

Testing Django applications

---

## coverage

Measure code coverage

---

# 4. Frontend Libraries

## Tailwind CSS

Purpose

Entire design system

Responsive layout

Dark mode

Utilities

---

## Alpine.js

Purpose

Small interactive components

Dropdowns

Modals

Tabs

Accordions

No SPA behavior

---

## HTMX

Purpose

Partial page updates

Search

Filters

Pagination

Inline editing

Avoids full page reloads while keeping server-rendered architecture.

---

## Heroicons

Purpose

Consistent SVG icon system.

---

## Chart.js

Purpose

Dashboard analytics

Sales

Purchases

Inventory

Revenue

---

## Tom Select

Purpose

Searchable select fields

Products

Suppliers

Categories

---

## SortableJS

Purpose

Future drag-and-drop support (optional for v1).

---

# 5. Typography

Font Family

```text
Inter
```

Fallback

```text
system-ui
```

Weights

300

400

500

600

700

800

---

# 6. Authentication

Use Django Authentication.

Features

Login

Logout

Password Reset

Session Authentication

Role Permissions

Groups

Decorators

Middleware

No JWT.

No OAuth.

No social login.

---

# 7. Authorization

Role-based access control.

Roles

Administrator

Inventory Manager

Sales Staff

Permissions enforced via:

* Django Groups
* Custom permissions
* View decorators
* Template permission checks

---

# 8. Database

Database Engine

PostgreSQL

Character Set

UTF-8

Timezone

UTC (stored)

Display in local timezone

UUID support

Enabled

Transactions

Atomic

Constraints

Enabled

Indexes

Optimized

---

# 9. Media Storage

Development

Local storage

```text
/media
```

Production

Configurable storage backend

Default implementation remains local.

---

# 10. Static Files

Development

```text
/static
```

Production

WhiteNoise

Compressed assets

Hashed filenames

---

# 11. Image Processing

Library

Pillow

Supported

JPEG

PNG

WEBP

Maximum Upload

5 MB

Auto resize

Generate thumbnails

Maintain aspect ratio

---

# 12. Search

Technology

PostgreSQL indexes

Django ORM

HTMX live search

No Elasticsearch.

No Meilisearch.

No Algolia.

---

# 13. Export System

Supported

CSV

Excel (.xlsx)

PDF

Print View

Libraries

openpyxl

ReportLab

---

# 14. Reporting Engine

Built with

Django ORM

Aggregation

Annotations

Chart.js

Exports

---

# 15. Forms

Django Forms

Server-side validation

Client-side enhancements

Inline validation

Error highlighting

---

# 16. Notifications

Toast notifications

Auto dismiss

Success

Warning

Error

Information

---

# 17. Security

Use

CSRF Protection

XSS Protection

SQL Injection Protection

Secure Cookies

Password Hashing

Session Security

Permission Checks

File Validation

MIME Validation

Input Sanitization

Rate limiting for authentication (via middleware or reverse proxy)

Never disable Django security middleware.

---

# 18. Logging

Python logging

Separate log files

Application

Errors

Security

Audit

Rotating logs

---

# 19. Performance

Use

select_related()

prefetch_related()

Database indexes

Pagination

Lazy loading where appropriate

Fragment caching (only if profiling shows benefit)

Avoid N+1 queries

---

# 20. Testing

Framework

pytest

Coverage

Minimum

```text
85%
```

Tests

Models

Views

Forms

Permissions

Services

Utilities

Integration

---

# 21. Code Quality

Formatter

Black

---

Linter

Ruff

---

Import sorting

Ruff (isort rules)

---

Type checking

mypy

---

Pre-commit hooks

Enabled

---

Docstrings

Google style

---

# 22. API Policy

Version 1

No REST API

No GraphQL

Server-rendered only

Future

Django Ninja or Django REST Framework

---

# 23. Background Jobs

Version 1

None

Future

Celery

Redis

---

# 24. Email

Backend

SMTP

Purpose

Password reset

User invitations (future)

Notifications (future)

---

# 25. Browser Support

Chrome

Edge

Firefox

Safari

Latest two major versions

---

# 26. Development Environment

IDE

VS Code

AI Coding Agent

Claude Code (Opus 4.8)

Operating System

Cross-platform

Windows

Linux

macOS

---

# 27. Git Standards

Branch Strategy

```text
main
develop
feature/*
bugfix/*
hotfix/*
```

Commit Convention

```text
feat:
fix:
refactor:
docs:
style:
test:
chore:
perf:
```

---

# 28. Environment Variables

```text
DEBUG

SECRET_KEY

ALLOWED_HOSTS

DATABASE_URL

EMAIL_HOST

EMAIL_PORT

EMAIL_HOST_USER

EMAIL_HOST_PASSWORD

EMAIL_USE_TLS

CSRF_TRUSTED_ORIGINS

TIME_ZONE

LANGUAGE_CODE
```

Never hardcode secrets.

---

# 29. Project Structure

```text
inventory_management/

├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│
├── apps/
│   ├── accounts/
│   ├── dashboard/
│   ├── products/
│   ├── categories/
│   ├── suppliers/
│   ├── purchases/
│   ├── sales/
│   ├── inventory/
│   ├── reports/
│   ├── audit/
│   ├── common/
│
├── templates/
│
├── static/
│
├── media/
│
├── tests/
│
├── requirements/
│
├── .env
│
├── manage.py
│
└── README.md
```

---

# 30. Libraries Explicitly Not Allowed

To keep the architecture consistent, the following are **not permitted** in Version 1:

* React
* Next.js
* Vue
* Angular
* jQuery
* Django REST Framework
* GraphQL
* FastAPI
* Flask
* MongoDB
* SQLite (production)
* Redis
* Celery
* Docker (required for development)
* Bootstrap
* Material UI
* Bulma
* Foundation
* AdminLTE
* DataTables

---

# 31. Engineering Standards

The AI coding agent **must** adhere to these rules throughout development:

* Follow Django MVT architecture.
* Keep business logic out of templates.
* Prefer service-layer functions for complex domain logic.
* Use transactions for all stock-changing operations.
* Never duplicate validation logic across layers.
* Optimize ORM queries before adding caching.
* Every model must define `__str__`.
* Every database table must include `created_at` and `updated_at`.
* Prefer UUID primary keys unless there is a documented reason not to.
* Use soft deletion only where the PRD explicitly requires it.
* All user-facing forms must include server-side validation.
* Permission checks are mandatory on every view, not just in navigation.
* Write tests for critical business rules, especially inventory calculations.
* Keep each Django app focused on a single domain responsibility.

---

## One important recommendation before Document 4

I would make **one significant improvement** to the overall architecture before moving on to the Frontend Guidelines:

Instead of using plain Django templates with scattered HTML, adopt a **component-based template architecture**. Create reusable components such as:

* `components/button.html`
* `components/card.html`
* `components/modal.html`
* `components/table.html`
* `components/input.html`
* `components/badge.html`
* `components/toast.html`
* `components/pagination.html`

