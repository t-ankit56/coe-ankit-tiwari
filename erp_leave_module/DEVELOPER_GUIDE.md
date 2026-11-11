# Developer Guide: build the leave app step by step

Audience: Claude Code (and the human reviewing it). Read `CLAUDE.md` and `SPEC.md` first. This guide says **how** to build what `SPEC.md` describes.

> **Layout note.** This guide was written for, and followed in, one folder. The project was then split into `backend/` and `frontend/`. Map the paths like this:
>
> | In this guide | Now |
> |---|---|
> | `manage.py`, `config/`, `leaves/`, `pytest.ini`, `requirements.txt`, `.env`, `.venv` | `backend/` |
> | `leaves/static/leaves/ts/` (TypeScript and `__tests__/`) | `frontend/src/` |
> | `leaves/static/leaves/html/`, `css/`, `img/` | `frontend/*.html`, `frontend/src/styles.css`, `frontend/public/` |
> | `npm run build` (tsc to `js/`) | `npm run typecheck` in `frontend/`. The pages run from the Vite dev server (`npm run dev`) instead of compiled JS. |
> | Django serves the pages | Vite serves them on port 5173 and forwards `/api` to Django |
> | A8 and the frontend tasks: empty HTML shells, `renderX(data): string`, `escapeHtml` | Later changed: full HTML pages, `partials/sidebar.html` included by a Vite plugin, `fillX`/`showX` functions writing into the DOM with `textContent`, permissions by the `hidden` attribute. `html.ts` is gone. See `CLAUDE.md` Frontend rules. |

## How to use this guide

1. Do the steps in order. Each step has **Do**, **Commits** and **Verify**.
2. Never start a step until the previous **Verify** passes.
3. Stop at every **CHECKPOINT** and report to the human (see `CLAUDE.md`, Working agreement).
4. Follow the red/green/refactor protocol in `CLAUDE.md` for every test.
5. Test names and ZOMBIES tags come from `SPEC.md` sections 12 to 14. Where this guide spells out exact inputs, use them. Where it points at `SPEC.md`, use the test names there.

---

# Part A: Reference (contracts you build against)

## A1. Versions and dependencies

- Python 3.12+, Django 5.2, djangorestframework 3.15+, `psycopg[binary]`, `python-dotenv`, `pytest`, `pytest-django`.
- Node 20+, `typescript`, `vitest`, `jsdom`.
- No other libraries without asking.

## A2. Rules layer contracts (`leaves/rules.py`)

Pure Python. No Django imports. No clock. No DB.

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping, Sequence

Holidays = Mapping[date, str]          # date -> holiday name, e.g. {date(2026, 11, 27): "Thanksgiving"}

@dataclass(frozen=True)
class DayInRange:
    date: date
    counts: Decimal                    # Decimal("1"), Decimal("0.5") or Decimal("0")
    label: str | None                  # None, "Weekend", or "<Holiday name>, not counted"

@dataclass(frozen=True)
class LeaveRecord:                     # what rules need to know about an existing request
    id: int | None
    start_date: date
    end_date: date
    half_day: bool
    status: str                        # "pending" | "approved" | "rejected"

@dataclass(frozen=True)
class SuggestedRequest:
    start_date: date
    end_date: date
    half_day: bool

@dataclass(frozen=True)
class MonthUsage:
    month: str                         # "2026-11"
    used: Decimal                      # already pending/approved in that month, before this request
    requested: Decimal                 # this request's counted days in that month
    left: Decimal                      # max(0, limit - used)
    over: Decimal                      # max(0, used + requested - limit)

@dataclass(frozen=True)
class ProbationStatus:
    ok: bool
    limit: Decimal
    months: list[MonthUsage]           # only months the request touches. Empty if not on probation.
    suggestion: SuggestedRequest | None

PROBATION_MONTHLY_LIMIT = Decimal("2")

def explain_each_day(start_date, end_date, holidays: Holidays, half_day=False) -> list[DayInRange]: ...
def count_working_days(start_date, end_date, holidays: Holidays, half_day=False) -> Decimal: ...
def find_overlapping_leave(start_date, end_date, existing: Sequence[LeaveRecord]) -> LeaveRecord | None: ...
def check_probation_limit(*, on_probation: bool, start_date, end_date, half_day: bool,
                          existing: Sequence[LeaveRecord], holidays: Holidays,
                          limit: Decimal = PROBATION_MONTHLY_LIMIT) -> ProbationStatus: ...
def suggest_largest_fitting_request(*, start_date, end_date, existing, holidays,
                                    limit=PROBATION_MONTHLY_LIMIT) -> SuggestedRequest | None: ...
```

Behaviour:
- A day counts 1 if Monday to Friday and not a holiday. Otherwise 0, with label `"Weekend"` or `"<name>, not counted"`. Both ends of the range are inclusive.
- `half_day=True` is valid only if `start_date == end_date` and that day counts. The day then counts `Decimal("0.5")`. Otherwise raise `HalfDayNeedsASingleWorkingDay`.
- `end_date < start_date` raises `EndDateIsBeforeStartDate`.
- `count_working_days` is the sum of `explain_each_day(...)` (reach this by refactor, see step 1.2).
- `find_overlapping_leave`: ignore `rejected`. Overlap means `start_date <= other.end_date and other.start_date <= end_date`. Return the clashing record or `None`.
- `check_probation_limit`: if not `on_probation`, return `ProbationStatus(ok=True, limit=limit, months=[], suggestion=None)`. Otherwise:
  - Compute the request's per-month counted days with `explain_each_day`.
  - Compute per-month `used` from existing records whose status is `pending` or `approved` (each record expanded with `explain_each_day(record.start_date, record.end_date, holidays, record.half_day)`).
  - Include a `MonthUsage` for each month the request's date range touches.
  - `ok` is true when every month has `over == 0`.
  - If not ok, set `suggestion` from `suggest_largest_fitting_request`, else `None`.
- `suggest_largest_fitting_request`: try end dates from `end_date` back down to `start_date` (full days, only candidates that count more than 0 days) and return the first that is ok in every month. If none fits and `start_date` is a working day, return a half day on `start_date` if that fits. Otherwise `None`. Use an internal helper that computes month usage, so this does not recurse into `check_probation_limit`.

## A3. Domain exceptions (`leaves/exceptions.py`)

Base class `LeaveError(Exception)`. Each takes no required arguments unless noted. `str(exc)` is the user-facing message.

| Exception | Message | HTTP (set in the handler) |
|---|---|---|
| `EndDateIsBeforeStartDate` | End date cannot be before start date. | 400 |
| `HalfDayNeedsASingleWorkingDay` | A half day needs a single working day. | 400 |
| `LeaveOverlapsExistingLeave(leave)` | You already have leave on {start}-{end}. | 400 |
| `ProbationLimitExceeded(status)` | This is over your probation limit. | 400 |
| `CommentRequiredToReject` | A comment is required to reject. | 400 |
| `NoApproverAssigned` | No approver is assigned to you. | 400 |
| `NotTheAssignedApprover` | Only the assigned approver can decide this request. | 403 |
| `LeaveRequestNotFound` | Leave request not found. | 404 |
| `LeaveAlreadyDecided` | This request has already been decided. | 409 |

`LeaveOverlapsExistingLeave` keeps the clashing leave as `.leave`. `ProbationLimitExceeded` keeps the status as `.status`.

## A4. Service contracts

```python
# leaves/services/leave_service.py
@dataclass
class LeavePreview: days: Decimal; breakdown: list[DayInRange]; overlap: LeaveRecord | None; probation: ProbationStatus | None
@dataclass
class MyLeaves: days_taken: Decimal; pending_count: int; leaves: list[LeaveRequest]

def preview_leave(user, start_date, end_date, half_day=False) -> LeavePreview
def submit_leave(user, start_date, end_date, half_day, reason) -> LeaveRequest
def list_my_leaves(user, today: date | None = None) -> MyLeaves

# leaves/services/approval_service.py
def list_waiting_approvals(approver) -> list[LeaveRequest]
def approve_leave(approver, leave_id) -> LeaveRequest
def reject_leave(approver, leave_id, comment) -> LeaveRequest
```

`preview_leave`:
- Raises the date errors from rules (invalid dates are a 400, not a preview).
- Overlap is **reported**, not raised. `probation` is `None` for users not on probation.

`submit_leave` checks in this order, inside `transaction.atomic()` with the user's profile row locked (`select_for_update`):
1. No approver, raise `NoApproverAssigned`.
2. Dates and half day, via `explain_each_day`.
3. Overlap, raise `LeaveOverlapsExistingLeave`.
4. Probation (only if on probation), raise `ProbationLimitExceeded`.
5. Create with `status="pending"`, `approver=profile.approver`, and `days` from the breakdown.

`list_my_leaves`: leaves newest first (`-created_at`, then `-id`). `days_taken` is the sum of `days` for **approved** requests whose `start_date.year == today.year`. `pending_count` counts all pending requests. `today` defaults to `timezone.localdate()`.

`approve_leave` and `reject_leave` check in this order: not found (404), not the assigned approver (403), already decided (409), then for reject a blank comment (400). `reject_leave` strips the comment before storing. Both set `decided_at = timezone.now()`.

`list_waiting_approvals`: pending requests where `approver == approver`, ordered by `start_date`, then `id`.

## A5. Backend plumbing

`config/settings.py` highlights:

```python
load_dotenv()
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
    "PASSWORD": os.environ["DB_PASSWORD"],
    "HOST": os.environ.get("DB_HOST", "localhost"), "PORT": os.environ.get("DB_PORT", "5432"),
}}
TIME_ZONE = "Asia/Kolkata"; USE_TZ = True
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["leaves.authentication.SessionAuthenticationWith401"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "leaves.exception_handler.translate_leave_errors_to_http",
    "COERCE_DECIMAL_TO_STRING": False,     # days are JSON numbers, not strings
}
```

`.env.example`: `DB_NAME=leaveapp`, `DB_USER=leaveapp`, `DB_PASSWORD=leaveapp`, `DB_HOST=localhost`, `DB_PORT=5432`.

`leaves/authentication.py`:
```python
class SessionAuthenticationWith401(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"      # makes DRF answer 401 instead of 403 for anonymous users
```

`leaves/permissions.py`: `IsApprover` allows only authenticated users whose `profile.is_approver` is true.

`leaves/exception_handler.py`: if the exception is a `LeaveError`, return `Response({"error": str(exc)}, status=<mapping from A3>)`. For DRF `ValidationError`, return 400 `{"error": "<first message>"}` (flatten field errors, for example `"reason: This field may not be blank."`). Otherwise defer to DRF's default handler.

Models (`leaves/models.py`):
- `Profile`: `user = OneToOneField(User, related_name="profile")`, `approver = ForeignKey(User, null=True, blank=True, related_name="direct_reports", on_delete=PROTECT)`, `on_probation`, `probation_until`. Add `CheckConstraint(condition=~Q(approver=F("user")), name="profile_approver_is_not_self")`. Add property `is_approver` that returns `self.user.direct_reports.exists()`.
- `Holiday`: `date` (unique), `name`.
- `LeaveRequest`: fields from `SPEC.md` section 5. `days = DecimalField(max_digits=4, decimal_places=1)`. `status` choices `pending`/`approved`/`rejected`. Add `Meta.ordering = ["-created_at", "-id"]` only if it does not hide a missing explicit `order_by` in services (services still order explicitly).
- Helper `to_leave_record(leave_request) -> rules.LeaveRecord` lives in `leaves/services/_records.py`.
- Holidays for rules: `{h.date: h.name for h in Holiday.objects.all()}` via a helper `load_holidays()` in `leaves/services/_records.py`.

Views and URLs:

| URL | View |
|---|---|
| `POST /api/login` | `LoginView` (`authentication_classes = []`, `permission_classes = [AllowAny]`). Authenticate with `authenticate(username=email, password=...)`, call `login(request, user)`, call `get_token(request)` so the cookie is set, return `CurrentUserSerializer`. Wrong credentials: raise `ValidationError` so it is a 400. |
| `POST /api/logout` | `LogoutView`, 204 |
| `GET /api/me` | `CurrentUserView`, decorated with `ensure_csrf_cookie` |
| `GET, POST /api/leaves` | `MyLeaveRequestsView` |
| `GET /api/leaves/preview` | `LeavePreviewView` |
| `GET /api/approvals` | `WaitingApprovalsView` (`IsApprover`) |
| `POST /api/leaves/<int:leave_id>/approve` | `ApproveLeaveView` |
| `POST /api/leaves/<int:leave_id>/reject` | `RejectLeaveView` |

Page routes (`leaves/pages.py`, `config/urls.py`): `/` → `my_leaves.html`, `/login` → `login.html`, `/apply` → `apply.html`, `/approvals` → `approvals.html`. Each view returns `FileResponse(open(path, "rb"), content_type="text/html")` from `leaves/static/leaves/html/`. No templates.

## A6. API payload examples

```jsonc
// GET /api/me and POST /api/login (200)
{"id": 1, "name": "Ankit Tiwari", "email": "ankit@incubyte.co",
 "is_approver": false, "on_probation": false, "approver": {"name": "Priya Nair"}}

// GET /api/leaves (200)
{"summary": {"days_taken": 5, "pending_count": 1},
 "leaves": [{"id": 4, "start_date": "2026-12-24", "end_date": "2026-12-28", "half_day": false,
             "days": 2, "reason": "Holiday", "status": "pending", "approver_name": "Priya Nair",
             "decision_comment": "", "submitted_at": "2026-11-02T10:00:00+05:30"}]}

// GET /api/leaves/preview?start_date=2026-11-19&end_date=2026-11-20&half=false (200, Aarav)
{"days": 2,
 "breakdown": [{"date": "2026-11-19", "counts": 1, "label": null},
               {"date": "2026-11-20", "counts": 1, "label": null}],
 "overlap": null,
 "probation": {"ok": false, "limit": 2,
               "months": [{"month": "2026-11", "used": 1.5, "requested": 2, "left": 0.5, "over": 1.5}],
               "suggestion": {"start_date": "2026-11-19", "end_date": "2026-11-19", "half_day": true}}}

// POST /api/leaves body
{"start_date": "2026-11-23", "end_date": "2026-11-27", "half_day": false, "reason": "Family trip"}
// -> 201 {"leave": {...Leave...}}

// errors
{"error": "You already have leave on 2026-11-18-2026-11-20."}
```

## A7. Test fixtures (`leaves/tests/`)

- `conftest.py`: `holidays` fixture (Thanksgiving 2026-11-27, Christmas 2026-12-25, New Year 2027-01-01 as DB rows), `people` fixture returning a namespace with `rohan`, `priya`, `ankit`, `aarav` (with the approver chain and Aarav on probation), `api_client` (`rest_framework.test.APIClient`), and `login_as(client, user)` (a real session login with `password123`).
- `factories.py`: `make_user(email, first_name, last_name, approver=None, on_probation=False)` and `make_leave(user, start_date, end_date, status="pending", half_day=False, days=None, reason="Test", approver=None)`. Compute `days` through the rules if not given.
- Pure rules tests build `LeaveRecord` objects and a plain dict of holidays. They need no fixtures.
- Use `force_authenticate` only for permission tests. Use real login for auth tests.
- Seed constants and test dates (2026): Mon 23 Nov, Thu 19 Nov, Fri 20 Nov, Fri 27 Nov (Thanksgiving), Fri 25 Dec (Christmas), Fri 1 Jan 2027 (New Year).

## A8. Frontend contracts (`leaves/static/leaves/ts/`)

`types.ts`: `CurrentUser`, `Leave`, `WaitingApproval`, `DayInRange`, `ProbationStatus`, `MonthUsage`, `LeavePreview`, `MyLeavesResponse`, `ApiErrorBody`. They mirror A6 exactly (`days` is `number`, dates are `string`).

`api.ts`:
```ts
export const navigation = { goTo(url: string) { window.location.assign(url); } };  // spy on this in tests
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function apiGet<T>(path: string): Promise<T>
export async function apiPost<T>(path: string, body?: unknown): Promise<T>   // adds X-CSRFToken from the csrftoken cookie
// 401 -> navigation.goTo("/login") and throw ApiError(401). Other non-2xx -> throw ApiError(status, body.error).
```

`html.ts`: `escapeHtml(text: string): string`.

`nav.ts`: `renderNav(me: CurrentUser, currentPath: string): string`. Always My leaves. Apply when `me.approver !== null`. Approvals when `me.is_approver`.

Page files: `login.ts`, `myLeaves.ts`, `apply.ts`, `approvals.ts`. Each runs only when `document.body.dataset.page` matches, so importing it in a test does nothing by itself:
```ts
if (typeof document !== "undefined" && document.body?.dataset.page === "login") initLogin();
```

HTML shells: `<body data-page="login">`, `<div id="nav"></div><main id="main"></main>`, a stylesheet link `/static/leaves/css/styles.css`, and `<script type="module" src="/static/leaves/js/login.js"></script>`.

---

# Part B: Build steps

## Step 0: Project setup (no tests)

**Do**
1. `git init`. Add `.gitignore` (`.env`, `.venv`, `node_modules`, `__pycache__`, `leaves/static/leaves/js/`, `.pytest_cache`). Commit: `chore: initial repo with spec docs` (include `SPEC.md`, `CLAUDE.md`, `DEVELOPER_GUIDE.md`).
2. Create the venv. Install Python dependencies from A1. Write `requirements.txt`.
3. `django-admin startproject config .` then `python manage.py startapp leaves`. Add `rest_framework` and `leaves` to `INSTALLED_APPS`. Apply the settings from A5.
4. Ask the human to run the Postgres setup from `SPEC.md` section 9 if `psql` access to `leaveapp` fails. Copy `.env.example` to `.env`.
5. Write the models from A5 and run `makemigrations` and `migrate`.
6. Write `pytest.ini`: `DJANGO_SETTINGS_MODULE = config.settings`, `testpaths = leaves/tests`, `addopts = --reuse-db -ra`.
7. Add `leaves/tests/test_database_connection.py` with one smoke test (marked `django_db`) that creates and reads a `Holiday`. Add the `conftest.py` and `factories.py` from A7 (fixtures only, no behaviour).
8. Frontend tooling: `package.json` (scripts `build: tsc`, `test: vitest run`), `tsconfig.json` (`target ES2020`, `module ES2020`, `moduleResolution Bundler`, `strict`, `rootDir leaves/static/leaves/ts`, `outDir leaves/static/leaves/js`, `exclude ["**/__tests__"]`), `vitest.config.ts` (`environment: "jsdom"`, `include: ["leaves/static/leaves/ts/**/*.test.ts"]`). Add a trivial `types.ts` so `tsc` has input.
9. Create the empty folder structure from `SPEC.md` section 6 and the four HTML shells (A8) with an empty `main`.
10. Write the `seed` management command (see step 1.9 for details, but at this point it can only create users, profiles and holidays).

**Commits**
- `chore: django, drf and postgres project skeleton`
- `chore: models and migrations for profile, holiday and leave request`
- `chore: pytest and vitest tooling`

**Verify:** `pytest` shows 1 passing, `npm run build` and `npm test` succeed (vitest may report no tests, which is fine), `python manage.py migrate` is clean.

> **CHECKPOINT 0.** Report to the human.

---

# Task 1: Apply for leave

Demo goal: Ankit logs in, applies for Mon 23 to Fri 27 Nov, and sees a Pending row counted as 4 days.

## Step 1.1: Rules stubs and spec

**Do**
1. Create `leaves/exceptions.py` (A3) and `leaves/rules.py` with the dataclasses from A2 and all functions stubbed to `raise NotImplementedError`. `check_probation_limit` and `suggest_largest_fitting_request` are included now so imports never break.
2. Read the `working_days` and `overlaps` ZOMBIES tables in `SPEC.md` sections 12.1 and 12.2. Update them if you change a row.

**Commits:** `chore: stub exceptions and rules functions`. Add a `docs: update spec for working days and overlaps` commit only if you changed a table.

**Verify:** `python -c "import leaves.rules"` works.

## Step 1.2: `count_working_days` and `explain_each_day`

File: `leaves/tests/test_rules_working_days.py`. Run each cycle with the red/green protocol. Holidays are a dict, `NO_HOLIDAYS = {}`.

| Tag | Test (see SPEC 12.1 for name) | Input | Expect | Simplest green |
|---|---|---|---|---|
| Z1 | single Sunday is zero | 2026-11-22 to 2026-11-22 | `Decimal("0")` | return `Decimal("0")` |
| Z2 | single holiday is zero | 2026-11-27, holidays `{2026-11-27: "Thanksgiving"}` | 0 | keep returning 0 only if it still passes; if O1 forces a change, revisit |
| O1 | single weekday is one | 2026-11-23 | 1 | return 1 if weekday < 5 else 0 |
| M1 | Mon to Fri is five | 2026-11-23 to 2026-11-27 | 5 | loop over dates |
| M2 | weekend inside range | 2026-12-24 to 2026-12-28, no holidays | 3 | already passes? If so, `test:` commit |
| M3 | holidays inside range (parametrize) | 23-27 Nov + Thanksgiving, 24-28 Dec + Christmas (2026-12-25) | 4 and 2 | skip holiday dates |
| B1 | starts and ends on weekend | 2026-11-21 to 2026-11-29 | 5 | likely already passes |
| B2 | crosses month end | 2026-11-30 to 2026-12-01 | 2 | likely already passes |
| B3 | crosses year end | 2026-12-31 to 2027-01-01 + New Year | 1 | likely already passes |
| B4 | half day on a working day | 2026-11-19, `half_day=True` | `Decimal("0.5")` | return 0.5 when half_day and the day counts |
| I1 | each day says whether it counts and why not | `explain_each_day` for 2026-11-21 to 2026-11-27 + Thanksgiving | 7 `DayInRange`: Sat/Sun `counts 0, label "Weekend"`; Mon to Thu `counts 1, label None`; Fri `counts 0, label "Thanksgiving, not counted"` | implement `explain_each_day` |
| E1 | end before start | 2026-11-24 to 2026-11-23 | `EndDateIsBeforeStartDate` | raise in `explain_each_day` |
| E2 | half day over several dates | 2026-11-23 to 2026-11-24, half | `HalfDayNeedsASingleWorkingDay` | raise |
| E3 | half day on weekend or holiday (parametrize) | 2026-11-22 half; 2026-11-27 half + Thanksgiving | `HalfDayNeedsASingleWorkingDay` | raise |

- After I1 is green, make one `refactor: count_working_days sums explain_each_day` commit, with all tests green.
- Put E1 to E3 on `count_working_days` (not just `explain_each_day`) so the public function is covered.

**Verify:** `pytest leaves/tests/test_rules_working_days.py` shows 14 test functions passing (parametrized cases expand).

## Step 1.3: `find_overlapping_leave`

File: `leaves/tests/test_rules_overlaps.py`. Build `LeaveRecord`s directly. Existing leave is Wed 18 to Fri 20 Nov 2026, `approved`, unless stated.

| Tag | Scenario | Expect |
|---|---|---|
| Z1 | existing list empty | `None` |
| O1 | new 2026-11-19 to 2026-11-19 against the existing record | returns that same record (assert identity or equality, not truthiness) |
| M1 | three records (a July one, the Nov one, a December one), new range 19-20 Nov | returns only the Nov record |
| B1 | new 2026-11-21 to 2026-11-23 (starts the day after the existing one ends) | `None` |
| B2 | new 2026-11-20 to 2026-11-23 (shares Fri 20 Nov) | returns the existing record |
| B3 | existing record has `status="rejected"`, new range overlaps it | `None` |

**Commits:** red/green pairs. **Verify:** 6 tests pass.

## Step 1.4: Model tests

File: `leaves/tests/test_models.py` (3 tests from `SPEC.md` 12.3). The self-approver test expects `IntegrityError` and must run inside `transaction.atomic()` (or `pytest.raises` around `Profile.objects.create` in an atomic block) so the connection is usable afterwards.

**Verify:** 3 tests pass. If the `CheckConstraint` is missing from the migration, this is the red that adds it (`makemigrations`).

## Step 1.5: Leave service

**Do (stub first):** create `leaves/services/__init__.py`, `leaves/services/_records.py` (`to_leave_record`, `load_holidays`) and `leaves/services/leave_service.py` with `preview_leave`, `submit_leave`, `list_my_leaves` stubbed. Read the service ZOMBIES table in `SPEC.md` first.

File: `leaves/tests/test_service_leaves.py` (8 tests from `SPEC.md` 12.4; the 3 probation tests come in Task 3). Fixtures: `people`, `holidays`.

| Tag | Arrange | Act | Assert |
|---|---|---|---|
| Z1 | `people.ankit` has no leaves | `list_my_leaves(ankit, today=date(2026,11,6))` | `leaves == []`, `days_taken == 0`, `pending_count == 0` |
| O1 | none | `submit_leave(ankit, 2026-11-23, 2026-11-27, False, "Family trip")` | `status == "pending"`, `approver == priya`, `days == Decimal("4.0")`, row saved |
| M1 | leaves for ankit (2) and aarav (1) | list for ankit | only ankit's, newest first |
| M2 | use the seeded-style set: ankit approved 8-10 Jul (3), approved 22-23 Oct (2), rejected 15 Jun (1), pending 24-28 Dec (2) | `list_my_leaves(ankit, today=date(2026,11,6))` | `days_taken == 5`, `pending_count == 1` |
| I1 | none | `preview_leave(ankit, 2026-11-23, 2026-11-27)` | `days == 4`, 5 breakdown rows, `probation is None`, `overlap is None` |
| E1 | ankit has approved 2026-11-18 to 2026-11-20 | submit 2026-11-20 to 2026-11-23 | `LeaveOverlapsExistingLeave`, `.leave` is the existing one |
| E2 | parametrize: end before start; half day over 2 dates | submit | `EndDateIsBeforeStartDate`; `HalfDayNeedsASingleWorkingDay` |
| E3 | `people.rohan` (no approver) | submit | `NoApproverAssigned`, nothing saved |

Implementation order follows the ZOMBIES order. Introduce `transaction.atomic()` and the profile lock during the E-phase refactor, not before a test needs it.

**Verify:** `pytest leaves/tests/test_service_leaves.py` passes (8).

## Step 1.6: Serializers, auth, views, exception handler

**Do (tests drive each piece)**

1. `test_api_auth.py` (6 tests, `SPEC.md` 12.5). Build `authentication.py`, `exception_handler.py`, `serializers.py` (`LoginInputSerializer`, `CurrentUserSerializer`), `views.py` (`LoginView`, `LogoutView`, `CurrentUserView`), `urls.py`. Notes:
   - Z1 forces `SessionAuthenticationWith401`: anonymous `GET /api/me` must be 401, not 403.
   - I2 asserts the response sets a `csrftoken` cookie on login.
   - Use a real `APIClient().post("/api/login", {...}, format="json")` for the login tests.
2. `test_api_leaves.py` (6 tests, `SPEC.md` 12.6). Add `LeaveSubmissionInputSerializer`, `LeavePreviewQueryInputSerializer`, `LeaveRequestSerializer`, `MyLeavesResponseSerializer`, `LeavePreviewSerializer`, `DayInRangeSerializer`, `MyLeaveRequestsView`, `LeavePreviewView`. Notes:
   - The reason field is `CharField` (trims whitespace), so whitespace-only fails validation (B1).
   - E2 is parametrized over overlap, invalid dates and no approver, all expecting 400 with an `error` message.
   - The preview `half` query parameter is a boolean, default false.
   - Write one test for each of the response shapes in A6 using `set(response.json().keys())`.

**Commits:** red/green per test, `refactor:` at the end (for example, extract a `serialize_preview` helper).

**Verify:** `pytest` shows all Task 1 backend tests passing. Total so far: 43 backend test functions (parametrized cases expand).

## Step 1.7: Seed command

**Do:** finish `leaves/management/commands/seed.py` (idempotent, `--reset`). Create the four users, profiles (approver chain, Aarav on probation until 2027-03-15), the three holidays, and the seeded requests from `SPEC.md` section 3. `days` comes from `count_working_days`. This is a tooling step: add one test `test_seed_is_idempotent` that runs the command twice and asserts counts are unchanged, in `leaves/tests/test_seed_command.py` (`green` only if the command already passes, otherwise a normal red/green pair).

**Verify:** `python manage.py seed && python manage.py seed` leaves 4 users, 3 holidays, 6 leave requests.

## Step 1.8: Frontend foundation

Work in `leaves/static/leaves/ts/`, tests in `__tests__/`.

| Order | File | Tests to write first (`SPEC.md` 12.7) |
|---|---|---|
| 1 | `html.ts` | `escapeHtml › turns a <script> tag in user text into harmless text` (also assert `&`, `"` and `'` are escaped) |
| 2 | `api.ts` | `post › sends the CSRF token from the cookie in the X-CSRFToken header`. Set `document.cookie = "csrftoken=abc"`, stub `fetch` with `vi.stubGlobal`, assert headers. |
| 3 | `api.ts` | `any call › redirects to the login page when the server answers 401`. Stub `fetch` to return 401, `vi.spyOn(navigation, "goTo")`. |
| 4 | `types.ts` | no test, copy the shapes from A6 |
| 5 | `login.ts` | `successful login › goes to My leaves without calling /api/me again`. Stub `fetch` for `/api/login` only, assert `navigation.goTo("/")` and that `fetch` was called once. |

**Verify:** `npm test` passes, `npm run build` compiles.

## Step 1.9: My leaves and Apply pages

| Order | File | Tests to write first |
|---|---|---|
| 1 | `nav.ts` | `nav › hides the Apply button when the user has no approver` |
| 2 | `myLeaves.ts` | `leaves table › shows "No requests yet" when there are none` |
| 3 | `myLeaves.ts` | `leaves table › shows one row per request with its status badge` |
| 4 | `apply.ts` | `apply page › shows the day count after valid dates are entered` |

Build notes:
- `renderLeavesTable(leaves: Leave[]): string` is pure. Rows show dates, days, status badge, approver, submitted date. Empty list shows "No requests yet".
- `renderSummaryCards(summary)` shows "Personal days taken in {year}" and "Requests waiting for approval".
- `initMyLeaves()` calls `/api/me`, draws the nav (with an Apply button only if allowed), then `/api/leaves`, then renders.
- `apply.ts`: form (start, end, half-day checkbox that is enabled only when start equals end, reason, read-only approver from `/api/me`). On any input change with both dates set, call `/api/leaves/preview` and render the "What this request uses" panel from the breakdown (day rows, total, green checks). Show the overlap message if `overlap` is not null. Submit calls `POST /api/leaves` then goes to `/`. Submit is disabled when dates are empty, the reason is blank, the preview failed, or `overlap` is not null.
- Write `styles.css` once, plain and small.

**Verify:** `npm test` shows 8 frontend tests passing for Task 1, `npm run build` is clean.

## Step 1.10: Refactor and demo

1. `refactor:` commit extracting the date parsing and error-response helpers (backend) if still duplicated.
2. `npm run build && python manage.py migrate && python manage.py seed && python manage.py runserver`.
3. Manual demo: log in as ankit@incubyte.co, click Apply, choose 23 to 27 Nov, see "4 working days" with Fri 27 Nov marked "Thanksgiving, not counted", enter a reason, submit, see a Pending row. Try 24 to 28 Dec and confirm the overlap message appears.

**Verify:** `pytest` (43 backend) and `npm test` (8) are green.

> **CHECKPOINT 1.** Report: test counts, tests that passed immediately, deviations. Print **AI log candidates**. Do not start Task 2 until the human says go.

---

# Task 2: Approvals

Demo goal: Priya approves one of Ankit's requests and rejects another with a comment, Ankit sees both. Then Priya applies for leave and Rohan approves it.

## Step 2.1: Approval service

**Do:** read the approvals ZOMBIES tables in `SPEC.md` (sections 13.1 and 13.2). Stub `leaves/services/approval_service.py` (`chore: stub approval service`).

File: `leaves/tests/test_service_approvals.py` (9 tests, `SPEC.md` 13.1). Arrange details:

| Tag | Arrange | Assert |
|---|---|---|
| Z1 | priya has no pending requests assigned | `list_waiting_approvals(priya) == []` |
| Z2 | none | `approve_leave(priya, 99999)` raises `LeaveRequestNotFound` |
| O1 | ankit pending request | after `approve_leave`: status approved, `decided_at` not None |
| O2 | ankit pending request | after `reject_leave(priya, id, "Release day")`: status rejected, `decision_comment == "Release day"` |
| M1 | priya's pending requests starting 2026-12-24, 2026-11-23, 2026-12-07, plus one decided, plus one pending assigned to rohan | list is only priya's pending ones, ordered 11-23, 12-07, 12-24 |
| B1 | parametrize approve and reject on an already decided request | `LeaveAlreadyDecided` |
| B2 | parametrize `""`, `"   "` | `CommentRequiredToReject`, status unchanged |
| E1 | ankit's request, `aarav` (not the approver) tries to approve | `NotTheAssignedApprover` |
| E2 | priya's own request (approver rohan), priya approves | `NotTheAssignedApprover` |

**Verify:** 9 tests pass.

## Step 2.2: Approval API

**Do:** add `IsApprover` (`permissions.py`), `WaitingApprovalSerializer`, `RejectionInputSerializer`, `WaitingApprovalsView`, `ApproveLeaveView`, `RejectLeaveView`, and URLs.

File: `leaves/tests/test_api_approvals.py` (8 tests, `SPEC.md` 13.2).
- E3: ankit (not an approver) listing approvals gets 403. E4 is parametrized over the three endpoints for anonymous 401.
- I1: after Priya rejects, Ankit's `GET /api/leaves` shows the `decision_comment`.
- Decided request: 409. Unknown id: 404. Reject without a comment: 400.

**Verify:** all backend tests pass (Task 1 plus 17 new).

## Step 2.3: Approvals frontend

| Order | File | Test (`SPEC.md` 13.3) |
|---|---|---|
| 1 | `approvals.ts` | `waiting list › shows "No requests waiting" when empty` |
| 2 | `approvals.ts` | `reject button › stays disabled until the comment has real text` (whitespace stays disabled) |
| 3 | `nav.ts` | `nav › shows the Approvals link only for approvers` |
| 4 | `myLeaves.ts` | `rejected request › shows the rejection comment under the dates, escaped` (comment `<b>x</b>` must not render as bold) |

Build notes:
- Left list sorted by start date as returned by the API. Click a row to fill the detail panel (requester, dates, days, reason, submitted). Comment box with label "Comment (required if you reject)". Approve calls `/approve`. Reject calls `/reject` and stays disabled until the trimmed comment is non-empty. After a decision, reload the list.
- Show server errors (403, 409) in a message area using `ApiError.message`.
- My leaves shows `decision_comment` under the dates for rejected requests, passed through `escapeHtml`.

**Verify:** `npm test` shows 12 frontend tests passing, `npm run build` is clean.

## Step 2.4: Refactor and demo

1. `refactor:` commits (for example, one shared helper for loading a leave and checking the approver).
2. Manual demo: log in as ankit, apply for 7 to 8 Dec. Log in as priya, open Approvals, approve it. Have Ankit apply again for 14 Dec, Priya rejects with a comment. Log in as ankit and confirm both statuses and the rejection comment. Log in as priya, confirm Apply is visible, apply for leave, log in as rohan, confirm Approvals shows Priya's request and Apply is hidden.

**Verify:** `pytest` (60 backend) and `npm test` (12) are green.

> **CHECKPOINT 2.** Report and print **AI log candidates**. Wait for the human.

---

# Task 3: Probation cap

Demo goal: Aarav tries Thu 19 to Fri 20 Nov, sees "1.5 of 2 days used", is blocked, clicks "Use 0.5 day on Thu 19 Nov", and submits.

## Step 3.1: Probation rules

**Do:** read the probation ZOMBIES tables in `SPEC.md` (section 14). The functions were stubbed in step 1.1.

File: `leaves/tests/test_rules_probation.py` (12 tests, `SPEC.md` 14.1). Use these shared constants:

```python
HOLIDAYS = {date(2026,11,27): "Thanksgiving", date(2026,12,25): "Christmas", date(2027,1,1): "New Year"}
AARAV_USED = [approved Mon 2 Nov (1 day), approved Tue 3 Nov half day (0.5)]   # 1.5 used in November
```

| Tag | Scenario | Expect |
|---|---|---|
| Z1 | `on_probation=False`, request Mon 9 to Fri 20 Nov (10 days) | `ok`, `months == []`, `suggestion is None` |
| Z2 | probation, no existing, request Mon 23 Nov | `ok`; Nov `used 0, requested 1, left 2, over 0` |
| O1 | probation, one approved day on Mon 2 Nov, request Mon 23 Nov | Nov `used 1, requested 1`, `ok` |
| M1 | `AARAV_USED`, request Thu 19 to Fri 20 Nov | `ok False`; Nov `used 1.5, requested 2, left 0.5, over 1.5` |
| B1 | `AARAV_USED`, request half day Thu 19 Nov | `ok True`; `over 0`; `used + requested == limit` |
| B2 | `AARAV_USED`, request full day Thu 19 Nov | `ok False`; `over 0.5` |
| B3 | existing: pending Mon 2 Nov, rejected Tue 3 Nov; request Thu 19 Nov | Nov `used == 1` |
| B4 | `AARAV_USED`, request Mon 30 Nov to Tue 1 Dec | `ok False`; months `["2026-11", "2026-12"]`; Nov `requested 1, over 0.5`; Dec `requested 1, over 0` |
| B5 | existing approved Thu 22 to Fri 23 Oct; request half day Thu 19 Nov | Nov `used 0`, `ok` |
| I1 | `AARAV_USED`, request Thu 19 to Fri 20 Nov | month entry has exactly `month, used, requested, left, over`; `limit == 2` |
| O2 | `AARAV_USED`, request Thu 19 to Fri 20 Nov | `suggestion == SuggestedRequest(2026-11-19, 2026-11-19, half_day=True)` |
| Z3 | existing approved Mon 2 and Tue 3 Nov (2.0 used), request Thu 19 Nov | `ok False`, `suggestion is None` |

Order the commits Z, O, M, B, I, E as in `CLAUDE.md`. O2 and Z3 are listed last but belong to the suggestion function, so write them after B5 and I1. `refactor:` once green: extract the shared month-usage helper used by both `check_probation_limit` and `suggest_largest_fitting_request`.

**Verify:** 12 tests pass.

## Step 3.2: Probation in services and API

**Do:** wire `check_probation_limit` into `preview_leave` (returns the status only when `on_probation`) and into `submit_leave` (step 4 of A4).

Tests:
- `test_service_leaves.py` adds 3 tests (`SPEC.md` 14.2): Aarav preview 19-20 Nov shows not ok with a suggestion; Aarav submit 19 Nov half day is created; Aarav submit 19-20 Nov raises `ProbationLimitExceeded` and creates nothing.
- `test_api_leaves.py` adds 1 test (`SPEC.md` 14.3): `POST /api/leaves` for Aarav 19-20 Nov returns 400 with the message "This is over your probation limit." even though no UI is involved.
- Serialize `ProbationStatusSerializer` and `MonthUsageSerializer` per A6. Make sure `Decimal` fields come out as numbers.

**Verify:** `pytest` shows 76 backend test functions passing.

## Step 3.3: Probation frontend

| Order | File | Test (`SPEC.md` 14.4) |
|---|---|---|
| 1 | `apply.ts` | `over the probation limit › shows the warning and disables Submit` |
| 2 | `apply.ts` | `suggestion button › fills in the dates and half-day box and refreshes the preview` |

Build notes:
- When `preview.probation && !preview.probation.ok`: replace the right panel with a red warning card ("This is over your probation limit", the explanatory line, and the suggestion button "Use {0.5 day} on {Thu 19 Nov}" when `suggestion` is not null). Below it show "Probation limit for {Month}" with `used of 2 days used`, a progress bar, `left`, a line for this request, and "{over} days over the limit if submitted as it is."
- Disable Submit and show "Change the dates to continue." beside it.
- The suggestion button sets the start date, end date and half-day checkbox from `suggestion`, then re-calls the preview.
- Optional, only if time allows: a "x of 2 days used this month" line on My leaves for users with `on_probation`. This needs no new endpoint if `/api/me` is extended, so skip it unless the human asks.

**Verify:** `npm test` shows 14 frontend tests passing, `npm run build` is clean.

## Step 3.4: Refactor and demo

1. `refactor:` commit (for example, extract `renderProbationCard`).
2. Manual demo: log in as aarav@incubyte.co, Apply, pick 19 to 20 Nov. Confirm the warning, "1.5 of 2 days used", 1.5 over, disabled Submit. Click "Use 0.5 day on Thu 19 Nov", confirm the panel turns green, submit, and see it Pending. Then try another day in November and confirm it is blocked (the month is now full). Try 30 Nov to 1 Dec and confirm November is flagged while December is fine.
3. Confirm Ankit is never blocked for any dates.

**Verify:** `pytest` (76 backend) and `npm test` (14 frontend) are green, giving 90 tests in total.

> **CHECKPOINT 3.** Report and print **AI log candidates**.

---

# Final step: wrap up

1. Review `SPEC.md`: make sure every ZOMBIES table and the decisions table (section 16) match what was built. Mark any rows not implemented as tests and say why.
2. `git log --oneline` check: every cycle has `red:` then `green:`, with the ZOMBIES tag and a readable name. List any `test:` commits (already passing) so the human can explain them.
3. Run the full suites one last time: `pytest`, `npm test`, `npm run build`.
4. Write a short `README.md`: prerequisites, Postgres setup, `.env`, install, migrate, seed, build, run, test, and the seeded logins.
5. Do **not** write `AI_LOG.md`. Give the human the combined **AI log candidates** from all checkpoints, plus these reminders for the walkthrough: commit history first, then the demos (Ankit, Priya and Rohan, Aarav), then what was cut, then one rejected suggestion.

> **DONE.** Final report to the human.

---

# Appendix: common pitfalls

| Pitfall | What to do |
|---|---|
| Anonymous requests return 403 | `SessionAuthenticationWith401` must be the default authentication class |
| `days` shows as `"4.0"` (string) | `COERCE_DECIMAL_TO_STRING = False`, and check serializer fields are `DecimalField` |
| Tests need a fresh DB each run | `--reuse-db` keeps it. Use `pytest --create-db` after changing migrations. |
| `IntegrityError` leaves the test transaction unusable | Wrap the failing call in `transaction.atomic()` inside `pytest.raises` |
| Vitest cannot resolve `./html.js` | Keep `moduleResolution: Bundler` and import with `.js`. Vite maps it to the `.ts` file. |
| `window.location.assign` not implemented in jsdom | Always go through `navigation.goTo` and spy on it |
| Today's date makes tests flaky | Pass `today=` into services. Never read the clock in rules. |
| A new test passes immediately | Commit it as `test:`. Do not fake a red. |
| Half day checkbox | Enabled only when start equals end. The server enforces it either way. |
| CSRF 403 on POST from the browser | Check `api.ts` reads the `csrftoken` cookie and `/api/me` is called on page load |
