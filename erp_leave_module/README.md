# Leave app

Apply for Personal leave, approve or reject it, and a probation cap of 2 days a month.
Django REST Framework backend, plain TypeScript frontend, PostgreSQL. Built test-first.

Two projects side by side:

- `backend/` is Django. It serves the JSON API on port 8000 and nothing else.
- `frontend/` is the TypeScript app. Its Vite dev server serves the pages on port **5173** and forwards `/api` to Django.

Read `SPEC.md` for what it does and every test by name, `DEVELOPER_GUIDE.md` for how it was built,
and `CLAUDE.md` for the working rules.

## Prerequisites

- Python 3.12 or newer
- Node 20 or newer (with npm)
- PostgreSQL, running locally

## Set up

### 1. Postgres

```
sudo -u postgres psql
CREATE USER leaveapp WITH PASSWORD 'leaveapp' CREATEDB;
CREATE DATABASE leaveapp OWNER leaveapp;
```

`CREATEDB` matters: pytest creates and drops its own `test_leaveapp` database and never touches your dev data.

### 2. Backend

```
cd backend
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed            # safe to run twice
python manage.py seed --reset    # wipe and reseed
```

The database defaults in `.env` match the Postgres commands above.
Replace `SECRET_KEY=change-me` with your own key:

```
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

`.env` is gitignored.

### 3. Frontend

```
cd frontend
npm install
```

## Run

Two terminals, both must be running.

```
# terminal 1
cd backend && . .venv/bin/activate && python manage.py runserver

# terminal 2
cd frontend && npm run dev
```

Open **http://localhost:5173/login**. Use port 5173, not 8000: Django no longer serves the pages.

Why it works on one origin: the dev server forwards `/api` to Django, so the session cookie and the
CSRF token behave as if there is a single site. Django trusts `http://localhost:5173` for CSRF
(`CSRF_TRUSTED_ORIGINS` in `backend/config/settings.py`).

A production build and deployment are not set up yet.

## Log in

The password for everyone is `password123` (local use only).

| Email | Role | Try this |
|---|---|---|
| `ankit@incubyte.co` | Employee, approver Priya | Apply for Mon 23 to Fri 27 Nov: 4 days, Thanksgiving not counted. Apply for 24 to 28 Dec: overlap with the pending request. |
| `aarav@incubyte.co` | Employee on probation, approver Priya | Apply for Thu 19 to Fri 20 Nov: over the probation limit. A warning shows, Submit stays enabled, and the suggestion offers 0.5 day. |
| `priya@incubyte.co` | Approver for Ankit and Aarav, her approver is Rohan | Open Approvals, approve one request, reject another with a comment. She can also apply. |
| `rohan@incubyte.co` | Approves for Priya, no approver | Approves Priya's request. Cannot apply. |

## Test

```
cd backend && . .venv/bin/activate && pytest     # 83 test functions (92 cases)
cd frontend && npm test                           # 16 tests (Vitest + jsdom)
cd frontend && npm run typecheck                  # type-checks the TypeScript
```

After changing a migration, run `pytest --create-db` once, because `pytest.ini` reuses the test database.

## Layout

```
backend/
  leaves/rules.py             pure calculations (working days, overlap, probation cap)
  leaves/services/            load data, call rules, write, raise domain exceptions
  leaves/serializers.py       shape and format validation only
  leaves/views.py             thin API views
  leaves/exception_handler.py domain exceptions to HTTP status and {"error": "..."}
  leaves/tests/               pytest tests
frontend/
  *.html                      page shells (login, my_leaves, apply, approvals)
  src/                        TypeScript, styles.css and the Vitest tests in __tests__/
  public/                     the logo
  vite.config.ts              dev server, the /api proxy and the page URLs
```

## Out of scope

Floating and Leave without pay, withdraw and cancel, team calendar, Slack and email notifications,
Contact HR, filters and tabs, the Decided tab, signup and password reset. The probation cap covers
Personal leave only, because Leave without pay does not exist here.
