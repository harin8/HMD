# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HMD is a Django 5.1 back-office management system for CA (Chartered Accountant) firms. It tracks clients' income-tax return status, TDS, certificates, proceedings, judgments, and timesheets, and produces reports. The codebase is server-rendered Django templates (no SPA/JS framework).

## Commands

The virtualenv is committed at `HMD_venv/`. Activate it first:

```bash
source HMD_venv/bin/activate          # uses Python 3.13
```

Common tasks (run from repo root):

```bash
python manage.py runserver            # dev server (Procfile uses --noreload on $PORT)
python manage.py migrate              # applies auth/permission migrations only (see below)
python manage.py setup_permissions    # (re)builds Groups + Permissions from accounts/roles.py
python manage.py createsuperuser      # superuser bypasses all permission checks

# Tests use Django's runner. There are currently no real tests (all tests.py are stubs).
python manage.py test                 # run all
python manage.py test <app>           # e.g. python manage.py test timesheet
python manage.py test <app>.tests.<TestCase>.<test_method>   # single test
```

## Critical architecture: dual database

This is the single most important thing to understand. The app uses **two databases simultaneously**:

1. **SQLite (Django ORM)** — used *only* for authentication and authorization: `auth_user`, `auth_group`, `auth_permission`, sessions, content types. The `accounts` app is the only app with real migrations. Every other app's `models.py` is an empty stub and has **no migrations** — do not add Django models for business data.

2. **MongoDB (pymongo)** — holds *all* business data. Each app has a `database.py` module that opens its own module-level client:

   ```python
   client = pymongo.MongoClient('mongodb://localhost/', 27017)
   db = client.HMD
   ```

   MongoDB must be running on `localhost:27017` with database `HMD`. The connection URI is **hardcoded** in every `database.py` (the `MONGO_URI` in `.env` is not actually read — see Gotchas).

Views import these `database.py` modules (often cross-app, e.g. `from proceedings import database as proc_database`) and call plain functions that return dicts/lists straight from Mongo, which are passed to templates. There is no ORM, no schema, and no repository layer over Mongo — functions issue `db.<collection>.find/insert/update` directly.

Key MongoDB collections (by usage): `clientMaster`, `proceedingsMaster`, `returnMaster`, `tdsMaster`, `otherFormsMaster`, `certificateMaster`, `partyMaster`, `groupCode`, `timesheetMaster`, `userProfiles`, `groupHead`, `judgmentsMaster`, `contactMaster`, `closedClientMaster`, plus `*Description` collections for dropdown/lookup data.

## Authentication & permission model

Authorization is role-based and spans both databases:

- **`accounts/roles.py`** is the source of truth. It defines `APP_PERMISSIONS` (per-app `view/add/change/delete`), `ROLE_PERMISSIONS` (which apps each role can touch), and `ROLE_HIERARCHY` (Super Admin → Super Group Head → Group Head → Senior Staff → Trainee). Editing roles/permissions means editing this file, then re-running `setup_permissions`.
- **`setup_permissions`** management command turns `roles.py` into Django `Group`s and synthetic `Permission`s (it creates a fake `appaccess` content type per app and permission codenames like `view_it_return`). It **deletes all existing permissions first**, so run it whenever roles change.
- **`accounts/middleware.py` (`PermissionMiddleware`)** runs on every request: redirects unauthenticated users to login, lets superusers through, and otherwise resolves the target view's app label and checks `<app>.view_<app>`. Failures redirect to `permission_denied`.
- **`accounts/decorators.py` (`@permission_required(app, type)`)** is applied per-view for finer-grained `add`/`change`/`delete` checks (middleware only gates `view`).
- **User profile data is split**: the Django `User` row holds credentials; a parallel `userProfiles` document in Mongo (`accounts/database.py`) holds `role`, `area`, `groups`, `designation`, `hourly_rate`/`rate_history`, and `timesheet_mandatory`. When creating/editing/deleting users in `accounts/views.py`, **both stores must be kept in sync**. Group-head assignments live in the Mongo `groupHead` collection.

## App / URL layout

Each business domain is a Django app mounted under a URL prefix in `HMD_Software/urls.py`. `IT_Return` is mounted at the root (`''`) and provides the landing/dashboard ("Live Board"). Apps: `accounts`, `IT_Return`, `clients`, `contacts`, `certificates`, `tds`, `other_forms`, `proceedings`, `judgments`, `insertions`, `reports`, `timesheet`, `costsheet`.

Within an app: `views.py` (logic), `urls.py` (routes), `database.py` (all Mongo access + date/format helpers), `templates/` (app-scoped), and often `templatetags/` (custom filters used heavily for display formatting). The shared base template is `templates/layout.html`.

## Conventions & gotchas

- **Dates**: timezone is `Asia/Kolkata`; the UI/DB convention is `DD-MM-YYYY` while ISO `YYYY-MM-DD` is used internally. `database.py` files contain conversion helpers (`date_to_IST_format`, `string_to_date`, etc.) — reuse them rather than re-parsing.
- **Timesheet**: `TIMESHEET_START_DATE` in settings (2025-04-01) bounds timesheet logic. `timesheet_mandatory` defaults to true for everyone *except* Super Admin / Super Group Head / Group Head (`accounts/database.py:is_timesheet_mandatory`).
- **`.env` is not loaded**: `settings.py` does not read environment variables. `SECRET_KEY`, `DEBUG=True`, and `ALLOWED_HOSTS=['*']` are hardcoded, and the Mongo URI is hardcoded in each `database.py`. Changing the committed `.env` has no effect; change `settings.py` / the `database.py` modules directly.
- **Reports**: `reports/request_data_retrieve.py` holds the report data-assembly logic, separate from `reports/database.py`.
- Static files served via WhiteNoise; deployment entrypoint is the `Procfile` (`runserver`, not gunicorn).

## Working with ECC on this project

The [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) plugin (`everything-claude-code@everything-claude-code`) is enabled. Reach for this curated subset on HMD — ignore the rest (Rust/Go/Kotlin/Laravel/healthcare/crypto/frontend skills don't apply here).

**Skills** (`Skill` tool): `django-security` (the role/permission model, auth across both DBs), `django-tdd` + `python-testing` (no real tests exist yet — write them here), `django-verification` (pre-PR gate), `python-patterns`, `database-migrations` (only the SQLite `accounts` app has real migrations), `security-review`, `codebase-onboarding`/`code-tour` (explain the dual-DB), `deployment-patterns` (Procfile/WhiteNoise).

**Agents** (`Agent` tool): `python-reviewer` (primary), `security-reviewer` (anything touching `auth_user` ↔ `userProfiles` sync or `roles.py`), `database-reviewer` (raw pymongo calls — no ORM safety net), `tdd-guide`, `silent-failure-hunter`, `performance-optimizer` (N+1 in Mongo report loops), `planner`/`architect`.

**UI/UX work — use `ui-ux-pro-max`, not ECC.** All front-end/visual/template work (the Live Board, tables, forms, layout in `templates/`, color/typography, accessibility) goes through the `ui-ux-pro-max` skill (suite: `ui-ux-pro-max`, `ckm:ui-styling`, `ckm:design-system`, `ckm:slides`, `ckm:design`, `ckm:brand`, `ckm:banner-design`). ECC's overlapping design skills (`design-system`, `frontend-patterns`, `frontend-slides`, `accessibility`, `liquid-glass-design`) are disabled via `skillOverrides` in `~/.claude/settings.json` to avoid conflicts.

**Caveat — `django-patterns` only partially applies:** HMD keeps all business data in MongoDB via `pymongo`, not the Django ORM. Use its middleware / signals / caching guidance; **ignore** its ORM-model, DRF-serializer, and migration advice for business data.

**Rules** auto-load from `~/.claude/rules/ecc/{common,python,web}/`. Hooks run via the plugin; TS/React-specific hooks are disabled for this Python repo through `env` vars in `~/.claude/settings.json` (`ECC_DISABLED_HOOKS`).
