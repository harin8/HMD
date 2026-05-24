# HMD — Architecture & Module Reference

A developer-facing map of the codebase: directory layout, what each module does, and the role/permission model. For a plain-language overview of *what the app is for*, see [README.md](README.md).

## Directory structure

```
HMD/
├── HMD_Software/        ← project core (settings, root URLs, static)
├── accounts/            ← users, login, roles & permissions
├── IT_Return/           ← income-tax returns + landing dashboard ("Live Board")
├── clients/             ← clients, parties, groups
├── contacts/            ← contact directory
├── certificates/        ← certificates (with PDF uploads)
├── tds/                 ← TDS (tax deducted at source) records
├── other_forms/         ← miscellaneous statutory forms
├── proceedings/         ← tax-department proceedings & court cases
├── judgments/           ← case rulings, summaries, citations
├── insertions/          ← master/lookup data (dropdown lists)
├── reports/             ← report generation
├── timesheet/           ← staff time logging
├── costsheet/           ← cost-of-work calculation
├── templates/           ← shared base template (layout.html)
├── static/ & staticfiles/ ← CSS/JS/images
├── HMD_venv/            ← committed Python virtual environment
├── manage.py            ← Django entry point
├── db.sqlite3           ← login/permission data only
└── Procfile / requirements.txt / .env
```

Every app folder follows the same internal layout:

- `views.py` — request handling / logic
- `urls.py` — routes
- `database.py` — all MongoDB access + date/format helpers
- `templates/` — the app's own pages
- `templatetags/` — custom display-formatting filters (most apps)

The `migrations/` folders are empty stubs everywhere **except `accounts`** — business data lives in MongoDB, not the Django ORM. SQLite (`db.sqlite3`) holds only authentication, authorization, and sessions.

## Modules

| Module | Mounted at | What it does |
|--------|-----------|--------------|
| **HMD_Software** | — | Project core: settings, the master URL list wiring all apps together, and shared static files. Not a feature itself. |
| **accounts** | `/accounts/` | User management: login/logout, creating/editing/deleting users, and the role-and-permission system controlling who can see and do what. |
| **IT_Return** | `/` (root) | The home landing page / dashboard, plus tracking of clients' income-tax returns — new returns, existing returns, CPC processing status, and group-wise filtering. |
| **clients** | `/clients/` | The client database — clients, "parties," and groups: creating, editing, closing/archiving, transferring parties between groups, and generating client codes. |
| **contacts** | `/contacts/` | A contact directory — add, edit, and list contact records. |
| **certificates** | `/certificates/` | Tracking certificates issued for clients, including uploading and viewing the PDF documents. |
| **tds** | `/tds/` | Records for TDS (tax deducted at source) — created per client, assessment year, quarter, and form type. |
| **other_forms** | `/other_forms/` | Handles miscellaneous statutory/tax forms not covered elsewhere, also with PDF attachments. |
| **proceedings** | `/proceedings/` | Tracks dealings with the tax department: regular proceedings, judicial proceedings, events/timeline within a case, marking case outcomes, and document viewing. |
| **judgments** | `/judgments/` | A library of case rulings — judgment records with summaries, legal citations, and attached PDFs. |
| **insertions** | `/insertions/` | Manages the master/lookup lists that feed dropdowns across the app (forum/author lists, certificate descriptions, other-form descriptions, proceedings descriptions). |
| **reports** | `/reports/` | Pulls data together into reports — both general and client-specific. |
| **timesheet** | `/timesheet/` | Staff log hours per client/task; includes assignment lookup, hour calculation, an "employee corner," and admin control over who is required to fill timesheets. |
| **costsheet** | `/costsheet/` | Generates a cost sheet — combining logged time with hourly rates to value the work done. |

## Roles & permissions

Defined in **`accounts/roles.py`** (the source of truth). There are **5 roles**, ranked by authority (1 = highest):

| # | Role | Access summary |
|---|------|----------------|
| 1 | **Super Admin** | Full access to everything, including full control over user accounts. |
| 2 | **Super Group Head** | Full access to all work modules; **read-only** on user accounts. |
| 3 | **Group Head** | Same as Super Group Head — full access to work modules, read-only on accounts. |
| 4 | **Senior Staff** | Full access (view/add/change/delete) to all work modules, but **no access to user accounts**. |
| 5 | **Trainee** | **View and add only** on work modules — cannot change or delete. **No access to reports and no access to accounts.** |

How permissions work in practice:

- Each module supports four permission types: **view, add, change, delete**.
- The difference between the top three roles is essentially their level of control over the **accounts** module (full vs. read-only).
- Senior Staff differ from Group Heads mainly in losing accounts access; Trainees are the most restricted — read/add only, and locked out of reports and accounts.
- A **superuser** (created via `createsuperuser`) bypasses all permission checks entirely.

Enforcement spans two layers:

- **`accounts/middleware.py`** gates whether a user can *view* a module at all.
- **`@permission_required` decorators** apply the finer add/change/delete checks per action inside views.

Changing roles or permissions means editing `accounts/roles.py`, then re-running `python manage.py setup_permissions` (which rebuilds the Django Groups/Permissions and **deletes existing permissions first**).
