# Phase 1 & 2 — Verification Checklist

Status legend: ✅ done & verified · ⚠️ needs your manual check · ⬜ deferred to a later phase (by design)

This checklist reflects the state after the verification pass. Automated checks
were run against SQLite in the sandbox (48 tests passing, 89% coverage on
`accounts` + `common`); items marked ⚠️ need a quick look in your browser
against PostgreSQL.

---

## How to verify on your machine

```bash
cd "/Users/abrarakhunji/Desktop/Hunny project"
source .venv/bin/activate

npm install            # fetches Alpine + HTMX, copies them into static/js/vendor/
npm run build          # vendor JS + build Tailwind CSS
python manage.py migrate
python manage.py sync_roles
python manage.py createsuperuser
python manage.py runserver

# Run the test suite (against your PostgreSQL)
pytest apps -v
coverage run -m pytest apps && coverage report
```

---

## Phase 1 — Project Foundation

### Project structure & config
- ✅ `manage.py`, `config/` (wsgi/asgi/urls) present and importable
- ✅ Settings split: `base.py` / `dev.py` / `prod.py`
- ✅ PostgreSQL configured via `DATABASE_URL` (django-environ)
- ✅ 9 domain apps scaffolded under `apps/`
- ✅ `manage.py check` passes with 0 issues
- ✅ Rotating file logging (app / error / security / audit)
- ✅ **Fixed:** static storage — manifest storage moved to `prod.py` only
  (was breaking dev/test rendering of `{% static %}`)

### Data foundation
- ✅ `common.BaseModel` (UUID PK + timestamps + created/updated_by)
- ✅ `ImmutableBaseModel` and `SoftDeleteModel` + soft-delete manager
- ✅ `common.validators.ImageFileValidator` (5 MB, JPEG/PNG/WEBP) — tested
- ✅ `common.exceptions` domain exception hierarchy

### Frontend toolchain
- ✅ Tailwind 4 with full design tokens (colors, 8-pt spacing, radii, Inter)
- ✅ Dark mode (class-based, no-flash inline script)
- ✅ **Fixed:** `app.css` rebuilt with all Phase 2 templates included
- ✅ **Fixed:** Alpine.js + HTMX now real npm deps, auto-copied to `vendor/`
  (were empty placeholder files)
- ⚠️ Confirm CSS looks correct in browser (run `npm run build` first)

### Base templates
- ✅ `base.html`, `base_app.html` (280px sidebar, 72px header, 1600px content)
- ✅ Error pages: 403 / 404 / 500 + shared error layout
- ✅ Partials: sidebar, header, footer, sidebar_link, breadcrumb, avatar
- ✅ All templates compile (verified via template loader)

---

## Phase 2 — Authentication & Authorization

### Models & migrations
- ✅ `Role` model (Administrator / Inventory Manager / Sales Staff)
- ✅ `User`: email login, UUID PK, `role` FK, `avatar`, `phone`
- ✅ **Fixed:** `User.created_by`/`updated_by` added (UserService wrote to
  fields that didn't exist — every service write was crashing)
- ✅ **Fixed:** `CustomUserManager` now filters soft-deleted users, so a
  deleted account is hidden AND cannot authenticate (was a security gap)
- ✅ Migrations 0001–0004; data migration seeds roles + groups on fresh DB
- ✅ No missing migrations (`makemigrations --check` clean)

### Permissions & bootstrapping
- ✅ Role→permission matrix (`accounts/permissions.py`)
- ✅ `sync_roles` command — idempotent, grants Admin all perms, skips
  not-yet-existing perms with a warning (re-run each future phase)
- ✅ Verified: fresh migrate → 3 roles + 3 groups; sync_roles runs clean

### Service layer
- ✅ `UserService`: create / assign_role (role↔group sync) / activate /
  deactivate / set_password — all atomic, all tested

### Access control
- ✅ `role_required` decorator + `RoleRequiredMixin`
- ✅ `LoginRequiredMiddleware` (auth-by-default + exempt list)
- ✅ `ActiveUserMiddleware` (immediate lockout on deactivation)
- ✅ **Fixed:** middleware redirect used a URL name as `next` (broken target)
- ✅ **Fixed:** `AllowAllUsersModelBackend` so inactive users get the correct
  "Account Disabled" message instead of "wrong password" (App Flow §3)

### Auth flows & UI
- ✅ Login by email, logout, remember-me (session expiry)
- ✅ Password reset chain (request → email → confirm → complete)
- ✅ Password change, profile edit, avatar upload
- ✅ Auth layout + all auth pages; profile/dashboard on app shell
- ✅ Sidebar: admin-only Users/Audit links; header profile dropdown + logout
- ⚠️ Confirm in browser: login, logout, profile edit, avatar upload,
  password change, dropdown, mobile sidebar, dark-mode toggle

### Tests
- ✅ 48 tests passing (models, services, auth, RBAC, middleware, validators,
  sync_roles, error views, template tags)
- ✅ 89% coverage on `apps/accounts` + `apps/common`

---

## Bugs found & fixed during verification

1. **UserService crash** — User model was missing `created_by`/`updated_by`
   that every service method wrote to. → added fields + migration 0004.
2. **Soft-deleted users could log in** — `CustomUserManager` didn't filter
   `is_deleted`. → added `get_queryset` filter (security fix).
3. **Static manifest storage in dev** — broke `{% static %}` everywhere.
   → moved WhiteNoise manifest storage to `prod.py`.
4. **Inactive-user login message wrong** — form's "disabled" message was
   unreachable. → switched to `AllowAllUsersModelBackend`.
5. **Broken middleware redirect** — passed a URL name as `next`.
   → use `request.get_full_path()`.
6. **Stale/empty frontend assets** — CSS built before Phase 2 templates;
   Alpine/HTMX were empty placeholders. → rebuilt CSS; npm-managed vendoring.

---

## Deferred to later phases (by design, not gaps)

- ⬜ Full dashboard (KPIs, charts) — Phase 8
- ⬜ User management UI (admin CRUD for users) — later phase
- ⬜ Business-model permissions granted by `sync_roles` — Phases 4–7
- ⬜ Global search, toasts wired to HTMX — later phases
- ⬜ Rate limiting on auth — deployment/proxy layer
