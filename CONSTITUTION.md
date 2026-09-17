# Project Constitution

Non-negotiable engineering rules for the Inventory Management System. Every
change must comply. These consolidate the rules stated across the Tech Stack,
Backend Schema, and Implementation Plan documents.

## Process

1. Never violate the PRD without explicit approval.
2. Complete exactly one phase at a time; never start a phase while the current
   one is incomplete or failing.
3. Keep every commit in a runnable state.
4. Never introduce a new dependency without justification; never add libraries
   from the "Not Allowed" list (Tech Stack §30).

## Architecture

5. Follow Django MVT plus an explicit service layer.
6. Never bypass the service layer for domain logic; views call services,
   services access models.
7. Never put business logic in templates.
8. Never duplicate business or validation logic across layers.
9. Never store inventory or financial logic in signals — keep it explicit in
   service methods and transactions.
10. Do not implement a repository pattern; use the ORM, custom QuerySets, and
    managers.

## Data & integrity

11. Every table uses a UUID primary key and timestamps.
12. Every stock-changing operation is atomic (`transaction.atomic()`) and locks
    the product row (`select_for_update()`).
13. Stock can never become negative.
14. Every stock change writes exactly one `StockMovement` row.
15. The stock ledger and audit log are immutable — never edited or deleted.
16. Completed purchases and sales are read-only.
17. Soft deletion is used only where the schema allows it (products, suppliers,
    categories, users).
18. Foreign keys enforce referential integrity; validation exists at the
    model, form, and service layers as appropriate.

## Quality

19. Permission checks are mandatory on every protected view — not just in
    navigation.
20. Write tests for every inventory-changing operation and critical business
    rule; maintain ≥ 85% coverage.
21. Never merge code that fails linting, formatting, or type checking.
22. Optimize ORM queries (`select_related`/`prefetch_related`) before adding
    caching; avoid N+1 queries.

## UI

23. Use reusable components only; never duplicate UI patterns.
24. No inline styles; follow the design tokens (spacing, radius, color,
    typography) exactly.
25. Every destructive action requires confirmation; errors inline, success via
    toast; every list paginates; every page has breadcrumbs.

## Style

26. Prefer readability over cleverness.
27. Every model defines `__str__`; docstrings use Google style where helpful.
28. Never hardcode URLs, permissions, or secrets.
