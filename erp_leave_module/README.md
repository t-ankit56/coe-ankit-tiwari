# Leave app

Apply for Personal leave, approve or reject it, and a probation cap of 2 days a month.
Django REST Framework backend, plain TypeScript frontend, PostgreSQL. Built test-first.

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

### 2. Environment file

```
cp .env.example .env
```

The database defaults match the Postgres commands above (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
Replace `SECRET_KEY=change-me` with your own key:

```
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

`.env` is gitignored.

### 3. Install

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm install
```

### 4. Create the tables and demo data

```
python manage.py migrate
python manage.py seed            # safe to run twice
python manage.py seed --reset    # wipe and reseed
```

### 5. Build the frontend and run

```
npm run build                    # compiles TypeScript to leaves/static/leaves/js/
python manage.py runserver
```

Open http://localhost:8000/login. Run `npm run build` again after changing any `.ts` file.

## Log in

The password for everyone is `password123` (local use only).

| Email | Role | Try this |
|---|---|---|
| `ankit@incubyte.co` | Employee, approver Priya | Apply for Mon 23 to Fri 27 Nov: 4 days, Thanksgiving not counted. Apply for 24 to 28 Dec: overlap with the pending request. |
| `aarav@incubyte.co` | Employee on probation, approver Priya | Apply for Thu 19 to Fri 20 Nov: over the probation limit. Click the suggestion for 0.5 day. |
| `priya@incubyte.co` | Approver for Ankit and Aarav, her approver is Rohan | Open Approvals, approve one request, reject another with a comment. She can also apply. |
| `rohan@incubyte.co` | Approves for Priya, no approver | Approves Priya's request. Cannot apply. |

## Test

```
pytest                           # backend: 83 test functions (92 cases)
npm test                         # frontend: 16 tests (Vitest + jsdom)
npm run build                    # type-checks the frontend
```

After changing a migration, run `pytest --create-db` once, because `pytest.ini` reuses the test database.

## Layout

```
leaves/rules.py            pure calculations (working days, overlap, probation cap)
leaves/services/           load data, call rules, write, raise domain exceptions
leaves/serializers.py      shape and format validation only
leaves/views.py            thin API views
leaves/exception_handler.py   domain exceptions to HTTP status and {"error": "..."}
leaves/static/leaves/      html shells, TypeScript in ts/, compiled JS in js/ (gitignored)
leaves/tests/              pytest tests
```

## Out of scope

Floating and Leave without pay, withdraw and cancel, team calendar, Slack and email notifications,
Contact HR, filters and tabs, the Decided tab, signup and password reset. The probation cap covers
Personal leave only, because Leave without pay does not exist here.
