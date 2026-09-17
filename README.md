# Inventory Management System (IMS)

A modern, server-rendered inventory management system built with Django 5.2,
PostgreSQL, and Tailwind CSS. Manage products, categories, suppliers,
purchases, sales, stock movements, and reporting from a single dashboard with
role-based access control.

> Status: **Phases 1 — 13 Complete (Production & Local Ready)**. All core
> modules, visual dashboards, reports, notification systems, audit log timelines,
> and testing suites have been successfully implemented and verified.

## Tech stack

| Layer     | Technology                              |
| --------- | --------------------------------------- |
| Language  | Python 3.13                             |
| Framework | Django 5.2 LTS                          |
| Database  | PostgreSQL 17                           |
| Frontend  | Django Templates + Tailwind CSS 4       |
| JS        | Vanilla ES + Alpine.js + HTMX           |
| Testing   | pytest + pytest-django + coverage       |
| Quality   | Black + Ruff + mypy + pre-commit        |

## Architecture

Modular, domain-oriented Django apps under `apps/`:

```
apps/
├── common/      # BaseModel, mixins, error views, shared utilities
├── accounts/    # users, roles, permissions, authentication
├── dashboard/   # KPIs, charts, recent activity
├── catalog/     # categories, products, suppliers
├── inventory/   # stock ledger, movements, adjustments
├── purchasing/  # purchases, purchase items
├── sales/       # sales, sale items, invoices
├── reporting/   # read-model reports and exports
└── audit/       # immutable audit log
```

Business logic lives in a **service layer**, not in views or templates. All
stock-changing operations run inside atomic transactions with row locking.
See [docs/Backend_Schema.md](docs/Backend_Schema.md).

## Prerequisites

- Python 3.13
- PostgreSQL 17 (running locally)
- Node.js + npm (for the Tailwind CSS build)

## Setup

```bash
# 1. Clone and enter the project
cd "Hunny project"

# 2. Create and activate a virtual environment (Python 3.13)
python3.13 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements/dev.txt

# 4. Configure environment
cp .env.example .env
#   Edit .env: set SECRET_KEY.
#   To use SQLite (simplest for local evaluation), set:
#   DATABASE_URL=sqlite:///db.sqlite3

# 5. Install frontend dependencies
npm install

# 6. Build the CSS
npm run build:css

# 7. Apply migrations
python manage.py migrate

# 8. Seed Demo Presentation Data (Highly Recommended)
python manage.py seed_demo_data
# This seeds prefilled products, suppliers, movements, POs, invoices, and logs.
# It also creates three preset testing accounts:
#   - Administrator: admin@example.com / password123!
#   - Inventory Manager: manager@example.com / password123!
#   - Sales Staff: staff@example.com / password123!

# 9. Run the development server
python manage.py runserver
```

Visit http://127.0.0.1:8000/ for the app and
http://127.0.0.1:8000/admin/ for the Django admin.

## Development workflow

```bash
npm run watch:css                # rebuild CSS on template changes
pytest                           # run the test suite
coverage run -m pytest && coverage report   # coverage (target: 85%+)
ruff check . && black --check .  # lint + format check
mypy .                           # type check
pre-commit install               # enable git hooks (run once)
```

## Documentation

All project documents live in [`docs/`](docs/):

- [PRD.md](docs/PRD.md) — product requirements
- [App_Flow.md](docs/App_Flow.md) — application flows
- [Tech_Stack.md](docs/Tech_Stack.md) — technology decisions
- [Frontend_Guidelines.md](docs/Frontend_Guidelines.md) — design system
- [Backend_Schema.md](docs/Backend_Schema.md) — data model & rules
- [Implementation_Plan.md](docs/Implementation_Plan.md) — phased roadmap
- [CONSTITUTION.md](CONSTITUTION.md) — non-negotiable engineering rules
