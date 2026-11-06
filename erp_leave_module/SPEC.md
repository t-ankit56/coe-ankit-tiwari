# Leave App: Spec

Django REST Framework backend, plain TypeScript frontend, PostgreSQL, built test-first in three sprint tasks.

---

## 1. Scope

**In**
1. Login (email and password only)
2. **Task 1:** My leaves (landing page) and Apply for Personal leave
3. **Task 2:** Approvals (approve, or reject with a required comment)
4. **Task 3:** Probation cap (2 days a month), shown as a warning that blocks submit

**Out (say so in the walkthrough)**
Floating and Leave-without-pay types, withdraw and cancel, team overlap view, Slack and email notifications, Contact HR, filters and tabs, Decided tab, signup, password reset, "which half" of a half day.

**Known limitation:** the screens say the cap covers Personal and Leave without pay together. Leave without pay is out of scope, so the cap covers Personal only.

---

## 2. Stack

| Part | Choice |
|---|---|
| Backend | Django + Django REST Framework |
| Database | PostgreSQL (system install) |
| Auth | Django session auth. Email is stored in `username`. |
| Frontend | Plain TypeScript compiled with `tsc` to JS. No framework, no bundler. |
| Serving | Django serves JSON, plus static HTML shells and the compiled JS from one origin (no CORS) |
| Backend tests | pytest + pytest-django |
| Frontend tests | Vitest + jsdom |

**Why TypeScript:** typed API contracts. If a Django response and a page disagree about a field, `tsc` fails at compile time instead of showing a blank cell in the browser.

**Why Django serves the HTML:** one origin means the session cookie and CSRF token work with no extra setup. The HTML files are empty shells. All rendering happens in TypeScript.

---

## 3. Users (seeded)

All seeded users share the dev password `password123`. This is for local use only.

| User | Email | Approver | Approves for | Can apply? | Notes |
|---|---|---|---|---|---|
| Ankit Tiwari | ankit@incubyte.co | Priya | nobody | Yes | Has past and pending requests |
| Aarav Singh | aarav@incubyte.co | Priya | nobody | Yes | On probation until 15 Mar 2027. 1.5 days used in Nov 2026. |
| Priya Nair (POD lead) | priya@incubyte.co | Rohan | Ankit, Aarav | Yes | Sees the Approvals page |
| Rohan Verma (Head of Core) | rohan@incubyte.co | none | Priya | **No** (no approver) | Sees the Approvals page |

**Rules about approvers**
- An approver is a normal user who can also apply for leave.
- A user can never be their own approver (database `CheckConstraint`).
- `is_approver` is derived: a user is an approver if anyone has them as their approver. It is not a stored flag.
- A user with no approver cannot apply. The API returns 400 and the UI hides the Apply button.

**Seeded requests**
- Ankit: 8-10 Jul (approved, 3 days), 22-23 Oct (approved, 2 days), 15 Jun (rejected, comment "Release day, I need the full team in."), 24-28 Dec (pending, 2 days).
- Aarav: Mon 2 Nov (approved, 1 day), Tue 3 Nov (approved, half day, 0.5).

**Seeded holidays:** Thanksgiving (Fri 27 Nov 2026), Christmas (Fri 25 Dec 2026), New Year (Fri 1 Jan 2027).

---

## 4. Business rules (the spec in one place)

1. Only Personal leave exists.
2. Days counted are working days. Saturdays, Sundays and seeded holidays count 0.
3. A half day is allowed only when start equals end and that date is a working day. It counts 0.5.
4. Start date cannot be after end date.
5. A reason is required. Whitespace alone does not count.
6. A new request cannot overlap your own pending or approved request. Rejected requests are ignored. Sharing a single day is an overlap (both ends inclusive).
7. The approver comes from the user's profile and cannot be changed in the app.
8. Only the assigned approver can decide a request, and only while it is pending. Decided requests are final.
9. Reject needs a comment. Whitespace alone does not count.
10. On probation, Personal leave is capped at 2 days per calendar month.
    - Pending and approved count toward the cap. Rejected does not.
    - A request spanning two months is checked against each month separately.
    - A request that exactly reaches 2.0 is allowed.
11. An over-cap request is refused by the server. The UI shows a warning, disables Submit, and offers the largest request that fits.
12. The suggestion is the largest request starting on the same start date that fits the days left. If only 0.5 is left, it is a half day on the start date. If nothing is left (or the start date is not a working day), there is no suggestion.

---

## 5. Data model

```
Profile        user (1:1 User), approver (FK User, null), on_probation (bool),
               probation_until (date, null)
               CheckConstraint: approver != user
Holiday        date (unique), name
LeaveRequest   user (FK), approver (FK), start_date, end_date, half_day (bool),
               days (Decimal(4,1), computed at submit), reason,
               status (pending | approved | rejected),
               decision_comment, created_at, decided_at (null)
```

---

## 6. Architecture and naming

### Layers

```
leaves/
  rules.py              # pure functions, no Django, no DB
  exceptions.py         # domain exceptions
  services/
    leave_service.py        # preview, submit, list my leaves
    approval_service.py     # list waiting, approve, reject
  serializers.py        # shape and format validation only
  permissions.py        # IsApprover
  authentication.py     # SessionAuthenticationWith401
  exception_handler.py  # translate_leave_errors_to_http
  views.py              # thin DRF APIViews
  models.py
  management/commands/seed.py
  static/leaves/
    html/               # login, my_leaves, apply, approvals (empty shells)
    ts/                 # api.ts, html.ts, types.ts, nav.ts, one file per page
    js/                 # tsc output (gitignored)
  tests/
tsconfig.json
package.json
vitest.config.ts
pytest.ini
.env.example
SPEC.md  CLAUDE.md  DEVELOPER_GUIDE.md
```

| Layer | Job | Must not |
|---|---|---|
| **rules** | Calculations: working days, overlap, probation | Touch the DB or Django |
| **services** | Load data, call rules, write, raise domain exceptions | Know about HTTP |
| **serializers** | Types, required fields, date format, non-blank text | Hold business rules |
| **views** | Authenticate, validate input, call a service, serialize output | Contain `if` logic about leave |

### Naming rules

The goal: someone who has never seen the code can read a name and know what is happening.

| Thing | Rule | Example |
|---|---|---|
| Test | `test_<situation>_<outcome>`, a plain sentence, no abbreviations, no ZOMBIES tags in the name | `test_rejecting_without_a_comment_is_refused` |
| Test file | `test_<layer>_<unit>.py` | `test_service_approvals.py` |
| View | `<Noun><Action>View`, one job each | `ApproveLeaveView` |
| Serializer | Input ends in `InputSerializer`, output ends in `Serializer` | `LeaveSubmissionInputSerializer` |
| Service function | `verb_noun`, a business action | `submit_leave`, `approve_leave` |
| Rules function | Says what it computes | `count_working_days` |
| Exception | Says what went wrong | `LeaveOverlapsExistingLeave` |
| Commit | `red: [Z1] <test in words>` | `red: [Z1] a single Sunday counts as zero days` |

**Rules functions:** `count_working_days`, `explain_each_day`, `find_overlapping_leave`, `check_probation_limit`, `suggest_largest_fitting_request`.

**Request and response fields** use `start_date` and `end_date`, because `from` is reserved in Python.

### Domain exceptions and HTTP mapping

One DRF exception handler (`translate_leave_errors_to_http`) turns these into responses shaped `{"error": "message"}`.

| Exception | HTTP |
|---|---|
| `EndDateIsBeforeStartDate`, `HalfDayNeedsASingleWorkingDay`, `LeaveOverlapsExistingLeave`, `ProbationLimitExceeded`, `CommentRequiredToReject`, `NoApproverAssigned` | 400 |
| `NotTheAssignedApprover` | 403 |
| `LeaveRequestNotFound` | 404 |
| `LeaveAlreadyDecided` | 409 |

**DRF gotcha:** `SessionAuthentication` returns 403 for anonymous users. `SessionAuthenticationWith401` defines `authenticate_header` so it returns 401.

---

## 7. Pages

| URL | Page | Who | Built in |
|---|---|---|---|
| `/login` | Email and password | Everyone | Task 1 |
| `/` | My leaves (landing): two summary cards (days taken this year, requests waiting) and a table of my requests, with a rejection comment under the dates | Logged in | Task 1 (comment in Task 2) |
| `/apply` | Apply for Personal leave: dates, half day, reason, read-only approver, live "What this request uses" panel | Users with an approver | Task 1, extended in Task 3 |
| `/approvals` | Waiting list sorted by start date, detail panel, comment box, Approve and Reject | Approvers | Task 2 |

**Nav (drawn by TypeScript from `/api/me`):** My leaves for everyone, Apply when `approver` is not null, Approvals when `is_approver` is true.

**Frontend rules**
- Every page calls `GET /api/me` first. A 401 redirects to `/login`. This also draws the nav.
- Exception: the login page redirects straight to `/` using the login response, with no extra call.
- `api.ts` sends the CSRF token (read from the `csrftoken` cookie) as `X-CSRFToken` on every POST.
- `html.ts` escapes all user text (reason, rejection comment).
- Each page file has a pure `renderX(data): string` and an `initX()` that fetches, renders and wires events.
- Working-day and cap logic lives only in Python. The Apply page calls the preview endpoint.
- Styling: one plain CSS file with a few colour variables. Polish is optional.

---

## 8. API endpoints

All endpoints take and return JSON with ISO dates (`"2026-11-19"`). Errors look like `{"error": "message"}`.

| # | Method and path | View | Task | Success | Errors |
|---|---|---|---|---|---|
| 1 | `POST /api/login` | `LoginView` | 1 | 200, the same payload as `/api/me`. Sets the `csrftoken` cookie. | 400 wrong credentials |
| 2 | `POST /api/logout` | `LogoutView` | 1 | 204 | none |
| 3 | `GET /api/me` | `CurrentUserView` | 1 | 200 `{id, name, email, is_approver, on_probation, approver: {name} or null}`. Uses `ensure_csrf_cookie`. | 401 |
| 4 | `GET /api/leaves` | `MyLeaveRequestsView` | 1 | 200 `{summary: {days_taken, pending_count}, leaves: [Leave]}` | 401 |
| 5 | `GET /api/leaves/preview?start_date=&end_date=&half=` | `LeavePreviewView` | 1, 3 | 200 `{days, breakdown, overlap, probation}` | 400 invalid dates, 401 |
| 6 | `POST /api/leaves` | `MyLeaveRequestsView` | 1, 3 | 201 `{leave}` | 400 invalid, overlap, no approver, over cap; 401 |
| 7 | `GET /api/approvals` | `WaitingApprovalsView` | 2 | 200 `[WaitingApproval]`, pending only, assigned to me, sorted by start date | 401, 403 not an approver |
| 8 | `POST /api/leaves/<id>/approve` | `ApproveLeaveView` | 2 | 200 `{leave}` | 401, 403, 404, 409 |
| 9 | `POST /api/leaves/<id>/reject` body `{comment}` | `RejectLeaveView` | 2 | 200 `{leave}` | 400 no comment, 401, 403, 404, 409 |

**Shapes**
```
Leave        = {id, start_date, end_date, half_day, days, reason, status,
                approver_name, decision_comment, submitted_at}
WaitingApproval = Leave + {requester_name, requester_email}
Day          = {date, counts, label}      // label: null, "Weekend" or "<Holiday>, not counted"
Overlap      = null | {start_date, end_date}
Probation    = null | {ok, limit: 2,
                       months: [{month: "2026-11", used, requested, left, over}],
                       suggestion: null | {start_date, end_date, half_day}}
```

**Why there is no CSRF endpoint:** the login view is public (DRF checks CSRF only for authenticated requests), Django's `login()` sets a fresh token cookie in its response, and `/api/me` re-sets it as a safety net after a reload.

### Serializers

| Serializer | Direction | Used by |
|---|---|---|
| `LoginInputSerializer` | In | `LoginView` |
| `CurrentUserSerializer` | Out | `LoginView`, `CurrentUserView` |
| `LeaveSubmissionInputSerializer` | In | `MyLeaveRequestsView.post` |
| `LeavePreviewQueryInputSerializer` | In | `LeavePreviewView` |
| `RejectionInputSerializer` | In | `RejectLeaveView` |
| `LeaveRequestSerializer` | Out | the Leave shape everywhere |
| `MyLeavesResponseSerializer` | Out | `{summary, leaves}` |
| `LeavePreviewSerializer` | Out | `{days, breakdown, overlap, probation}` |
| `DayInRangeSerializer` | Out | one breakdown row |
| `ProbationStatusSerializer` | Out | month-by-month status and suggestion |
| `WaitingApprovalSerializer` | Out | leave plus requester |

---

## 9. PostgreSQL setup

```sql
sudo -u postgres psql
CREATE USER leaveapp WITH PASSWORD 'leaveapp' CREATEDB;
CREATE DATABASE leaveapp OWNER leaveapp;
```

- `CREATEDB` matters because pytest-django creates and drops its own `test_leaveapp` database. It never touches dev data.
- Install `psycopg[binary]` and `python-dotenv`.
- `config/settings.py` reads `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` from `.env`. Commit `.env.example`, gitignore `.env`.
- `pytest.ini` sets `DJANGO_SETTINGS_MODULE` and `addopts = --reuse-db`.
- Day counts use `DecimalField(max_digits=4, decimal_places=1)` so 0.5 is exact.
- Pure-rules tests have no `django_db` mark and never touch the database. Service and API tests use `@pytest.mark.django_db`.
- The seed command is idempotent. `python manage.py seed --reset` wipes and reseeds.

---

## 10. Test method: ZOMBIES

For each unit, write tests in this order. Each test is a `red:` commit (failing) then a `green:` commit (passing).

| Letter | Meaning | Examples |
|---|---|---|
| **Z** | Zero | empty list, no requests, nothing used |
| **O** | One | one request, one weekday, one approval |
| **M** | Many | several requests, a full week, several holidays |
| **B** | Boundaries | same-day range, month end, year end, exactly at the cap |
| **I** | Interfaces | response shapes, status codes, labels |
| **E** | Exceptions | invalid input, forbidden, unauthenticated |

- The letter goes in the commit message and in the tables in sections 12 to 14, not in the test name.
- Zero and One force the simplest implementation. Many forces the loop. Boundaries and Exceptions harden it.
- Business rules are tested once, at the service or rules level. API tests check only status codes, response shape and auth.

---

## 11. Step 0: setup (no tests)

1. Create the Django project `config` and app `leaves`. Install Django, DRF, pytest, pytest-django, `psycopg[binary]`, `python-dotenv`.
2. Create the Postgres user and database (section 9).
3. Write models and migrations (section 5).
4. Write the `seed` command (section 3).
5. Frontend tooling: `package.json` with `typescript`, `vitest`, `jsdom`. `tsconfig.json` with output to `static/leaves/js/`. Scripts: `npm run build`, `npm test`.
6. Add a smoke test that the DB connects and migrations run.
7. Commit: `chore: project setup`.

---

## 12. Task 1: Apply for leave

**Demo:** Ankit logs in, applies for Mon 23 to Fri 27 Nov, sees a Pending row counted as 4 days (Thanksgiving not counted).

**Build order:** rules, models, services, serializers and views, login and `api.ts`/`html.ts`, My leaves page, Apply page, refactor.

### 1.1 `test_rules_working_days.py` (14)

| Tag | Test | Expectation |
|---|---|---|
| Z1 | `test_a_single_sunday_counts_as_zero_days` | Sun 22 Nov = 0 |
| Z2 | `test_a_single_public_holiday_counts_as_zero_days` | Fri 27 Nov with Thanksgiving = 0 |
| O1 | `test_a_single_weekday_counts_as_one_day` | Mon 23 Nov = 1 |
| M1 | `test_monday_to_friday_counts_as_five_days` | 23-27 Nov, no holidays = 5 |
| M2 | `test_a_weekend_inside_the_range_is_not_counted` | Thu 24 to Mon 28 Dec, no holidays = 3 |
| M3 | `test_public_holidays_inside_the_range_are_not_counted` (parametrized) | 23-27 Nov with Thanksgiving = 4. 24-28 Dec with Christmas = 2. |
| B1 | `test_range_starting_and_ending_on_a_weekend_counts_only_the_weekdays` | Sat 21 to Sun 29 Nov = 5 |
| B2 | `test_range_crossing_a_month_end_is_counted_across_both_months` | Mon 30 Nov to Tue 1 Dec = 2 |
| B3 | `test_range_crossing_a_year_end_is_counted_across_both_years` | Thu 31 Dec to Fri 1 Jan with New Year = 1 |
| B4 | `test_a_half_day_on_a_working_day_counts_as_half_a_day` | Thu 19 Nov half = 0.5 |
| I1 | `test_each_day_says_whether_it_counts_and_why_not` | `explain_each_day` returns one row per date with `counts` and `label` |
| E1 | `test_end_date_before_start_date_is_refused` | `EndDateIsBeforeStartDate` |
| E2 | `test_a_half_day_over_more_than_one_date_is_refused` | `HalfDayNeedsASingleWorkingDay` |
| E3 | `test_a_half_day_on_a_weekend_or_holiday_is_refused` | `HalfDayNeedsASingleWorkingDay` |

`count_working_days` is the sum of `explain_each_day`. The breakdown drives the right-hand "What this request uses" panel, for example for 21-27 Nov: Sat 0 "Weekend", Sun 0 "Weekend", Mon 1 ... Fri 0 "Thanksgiving, not counted".

### 1.2 `test_rules_overlaps.py` (6)

`find_overlapping_leave` returns the clashing request (not just a boolean) so the error message can name the dates. The rule is `new.start <= existing.end and existing.start <= new.end`, both ends inclusive.

| Tag | Test | Expectation |
|---|---|---|
| Z1 | `test_no_existing_leave_means_no_overlap` | None |
| O1 | `test_returns_the_existing_leave_that_overlaps` | Returns that exact request |
| M1 | `test_returns_only_the_clashing_leave_when_there_are_several` | Returns the right one |
| B1 | `test_leave_ending_the_day_before_does_not_overlap` | Existing ends 20 Nov, new starts 21 Nov: None |
| B2 | `test_leave_sharing_one_day_does_overlap` | Existing Wed 18 to Fri 20 Nov, new Fri 20 to Mon 23 Nov: returns existing |
| B3 | `test_rejected_leave_is_ignored` | None |

### 1.3 `test_models.py` (3)

| Tag | Test |
|---|---|
| Z1 | `test_a_user_without_an_approver_is_allowed` |
| E1 | `test_a_user_cannot_be_their_own_approver` (IntegrityError) |
| I1 | `test_user_is_an_approver_only_if_someone_has_them_as_approver` |

### 1.4 `test_service_leaves.py` (9 in Task 1)

| Tag | Test | Expectation |
|---|---|---|
| Z1 | `test_new_user_with_no_requests_gets_an_empty_list_and_zero_summary` | `[]`, 0, 0 |
| O1 | `test_submitting_leave_creates_a_pending_request_with_the_profile_approver_and_counted_days` | 23-27 Nov: 4 days, approver Priya, status pending |
| M1 | `test_my_leaves_lists_only_my_requests_newest_first` | Others excluded |
| M2 | `test_summary_counts_approved_days_this_year_and_pending_requests` | Seeded Ankit: 5 days taken, 1 pending |
| I1 | `test_preview_returns_days_and_breakdown_with_no_probation_status_for_regular_user` | `probation` is null |
| I2 | `test_preview_reports_the_clashing_leave_instead_of_refusing` | `overlap` is the existing request, no exception (added during build: the Apply page needs it) |
| E1 | `test_submitting_overlapping_leave_is_refused_and_names_the_clashing_dates` | `LeaveOverlapsExistingLeave` |
| E2 | `test_submitting_invalid_dates_is_refused` (parametrized) | End before start. Half day over several dates. |
| E3 | `test_submitting_without_an_approver_is_refused` | Rohan: `NoApproverAssigned` |

### 1.5 `test_api_auth.py` (6)

| Tag | Test |
|---|---|
| Z1 | `test_me_without_logging_in_returns_401` |
| O1 | `test_login_returns_the_same_user_details_as_me` |
| I1 | `test_me_shows_the_approver_and_whether_i_am_an_approver` (Ankit: not approver. Priya: approver, with Rohan as approver.) |
| I2 | `test_login_sets_the_csrf_cookie` |
| E1 | `test_login_with_a_wrong_password_returns_400` |
| E2 | `test_after_logout_me_returns_401` |

### 1.6 `test_api_leaves.py` (6 in Task 1)

| Tag | Test |
|---|---|
| Z1 | `test_my_leaves_response_has_a_summary_and_a_list` |
| O1 | `test_submitting_leave_returns_201_with_the_created_request` |
| B1 | `test_a_whitespace_only_reason_returns_400` |
| I1 | `test_preview_returns_days_and_a_day_by_day_breakdown` |
| E1 | `test_submitting_leave_without_logging_in_returns_401` |
| E2 | `test_overlap_invalid_dates_and_missing_approver_each_return_400` (parametrized) |

### 1.7 Frontend (9)

| File | Test |
|---|---|
| `html.test.ts` | `escapeHtml › turns a <script> tag in user text into harmless text` |
| `api.test.ts` | `post › sends the CSRF token from the cookie in the X-CSRFToken header` |
| `api.test.ts` | `any call › redirects to the login page when the server answers 401` |
| `login.test.ts` | `successful login › goes to My leaves without calling /api/me again` |
| `myLeaves.test.ts` | `leaves table › shows "No requests yet" when there are none` |
| `myLeaves.test.ts` | `leaves table › shows one row per request with its status badge` |
| `nav.test.ts` | `nav › hides the Apply button when the user has no approver` |
| `nav.test.ts` | `nav › shows the Apply button when the user has an approver` (added during build: the hide-only test cannot force Apply to ever appear) |
| `apply.test.ts` | `apply page › shows the day count after valid dates are entered` |

### 1.8 Finish

`refactor:` commit (extract date parsing and the error-response helper), run `seed`, do the demo.

**Task 1 total: 44 backend + 9 frontend = 53.**

---

## 13. Task 2: Approvals

**Demo:** Priya approves one of Ankit's requests and rejects another with a comment. Ankit sees both results. Then Priya applies for leave herself and Rohan approves it.

### 2.1 `test_service_approvals.py` (9)

| Tag | Test | Expectation |
|---|---|---|
| Z1 | `test_no_waiting_requests_gives_an_empty_list` | `[]` |
| Z2 | `test_deciding_a_request_that_does_not_exist_is_refused` | `LeaveRequestNotFound` |
| O1 | `test_approving_moves_a_pending_request_to_approved_and_records_when` | Status approved, `decided_at` set |
| O2 | `test_rejecting_with_a_comment_moves_it_to_rejected_and_stores_the_comment` | Status rejected |
| M1 | `test_waiting_list_shows_only_my_pending_requests_sorted_by_start_date` | Decided and other approvers' requests excluded |
| B1 | `test_a_request_that_was_already_decided_cannot_be_decided_again` (parametrized approve and reject) | `LeaveAlreadyDecided` |
| B2 | `test_a_blank_or_whitespace_only_comment_is_refused` (parametrized) | `CommentRequiredToReject` |
| E1 | `test_only_the_assigned_approver_can_decide` | `NotTheAssignedApprover` |
| E2 | `test_an_approver_cannot_decide_their_own_request` | Priya on her own request (assigned to Rohan) is refused |

### 2.2 `test_api_approvals.py` (8)

| Tag | Test |
|---|---|
| Z1 | `test_deciding_an_unknown_request_returns_404` |
| O1 | `test_approving_returns_200_with_the_updated_request` |
| B1 | `test_deciding_an_already_decided_request_returns_409` |
| I1 | `test_requester_sees_the_rejection_comment_in_my_leaves` |
| E1 | `test_rejecting_without_a_comment_returns_400` |
| E2 | `test_a_different_approver_deciding_returns_403` |
| E3 | `test_a_user_who_is_not_an_approver_listing_approvals_returns_403` |
| E4 | `test_all_approval_endpoints_return_401_when_not_logged_in` (parametrized over the 3 endpoints) |

### 2.3 Frontend (4)

| File | Test |
|---|---|
| `approvals.test.ts` | `waiting list › shows "No requests waiting" when empty` |
| `approvals.test.ts` | `reject button › stays disabled until the comment has real text` |
| `nav.test.ts` | `nav › shows the Approvals link only for approvers` |
| `myLeaves.test.ts` | `rejected request › shows the rejection comment under the dates, escaped` |

**Build:** `approval_service.py`, the three approval views, `approvals.ts` (list, detail panel, comment box, buttons), the nav link, and rejection comments on My leaves. Finish with a `refactor:` commit and the demo.

**Task 2 total: 17 backend + 4 frontend = 21.**

---

## 14. Task 3: Probation cap

**Demo:** Aarav tries Thu 19 to Fri 20 Nov and sees "1.5 of 2 days used". The request is 2 days, so it is 1.5 over and Submit is disabled. He clicks "Use 0.5 day on Thu 19 Nov", submits, and it succeeds.

### 3.1 `test_rules_probation.py` (12)

| Tag | Test | Expectation |
|---|---|---|
| Z1 | `test_user_not_on_probation_is_never_limited` | ok, even at 10 days |
| Z2 | `test_first_one_day_request_of_a_month_is_within_the_limit` | ok, 1 left |
| O1 | `test_existing_leave_in_the_same_month_counts_towards_the_limit` | 1 used, 1 requested: ok |
| M1 | `test_two_day_request_with_one_and_a_half_days_used_is_over_by_one_and_a_half` | Aarav's screen |
| B1 | `test_request_that_exactly_reaches_the_limit_is_allowed` | 1.5 used, 0.5 requested: ok, 0 left |
| B2 | `test_one_day_request_with_one_and_a_half_days_used_is_over_by_half_a_day` | over 0.5 |
| B3 | `test_pending_leave_counts_but_rejected_leave_does_not` | Only pending and approved summed |
| B4 | `test_request_spanning_two_months_is_checked_against_each_month` | 1.5 used in Nov, Mon 30 Nov to Tue 1 Dec: Nov over 0.5, Dec ok |
| B5 | `test_leave_in_other_months_is_ignored` | October usage does not affect November |
| I1 | `test_result_reports_used_requested_left_and_over_for_each_month` | Matches the Probation shape |
| O2 | `test_suggestion_is_the_largest_request_that_fits_the_days_left` | 0.5 left, start 19 Nov: half day on 19 Nov |
| Z3 | `test_no_suggestion_when_no_days_are_left` | `suggestion` is null |

### 3.2 `test_service_leaves.py` (3 added)

| Tag | Test |
|---|---|
| O2 | `test_preview_shows_probation_status_and_suggestion_for_user_on_probation` (Aarav 19-20 Nov: over 1.5, with a suggestion) |
| B1 | `test_submitting_leave_that_exactly_reaches_the_probation_limit_is_created` (19 Nov half day: created) |
| E4 | `test_submitting_leave_over_the_probation_limit_is_refused` (`ProbationLimitExceeded`) |

### 3.3 `test_api_leaves.py` (1 added)

| Tag | Test |
|---|---|
| E3 | `test_submitting_leave_over_the_probation_limit_returns_400_even_without_the_ui` |

### 3.4 Frontend (2)

| File | Test |
|---|---|
| `apply.test.ts` | `over the probation limit › shows the warning and disables Submit` |
| `apply.test.ts` | `suggestion button › fills in the dates and half-day box and refreshes the preview` |

**Build:** wire `check_probation_limit` into the preview and `submit_leave`. On the Apply page add the red warning card ("This is over your probation limit"), the "Probation limit for November" breakdown, the helper text next to the disabled Submit, and the suggestion button. Optional: a small "x of 2 used this month" line on My leaves for probation users. Finish with a `refactor:` commit and the demo.

**Task 3 total: 16 backend + 2 frontend = 18.**

---

## 15. Totals

| | Backend | Frontend | Total |
|---|---|---|---|
| Task 1 | 44 | 9 | 53 |
| Task 2 | 17 | 4 | 21 |
| Task 3 | 16 | 2 | 18 |
| **All** | **77** | **15** | **92** |

Parametrized tests count once. If time is short, merge the API shape tests in `test_api_leaves.py` (Z1, O1, I1) into one and drop `test_api_approvals` I1, since the service layer already covers it. That brings the total to about 75 without dropping any ZOMBIES letter.

---

## 16. Spec decisions

| Question | Decision |
|---|---|
| Which leave types does the cap cover? | Personal only (Leave without pay is out of scope). |
| Which statuses count toward the cap? | Pending and approved. Rejected does not. |
| Request spans two months? | Checked per calendar month. |
| Half day? | Counts 0.5. Single working date only. No "which half" is stored. |
| Exactly 2.0 in a month? | Allowed. |
| Overlap with my own request? | Refused if the other is pending or approved. Rejected is ignored. |
| Who can decide? | Only the assigned approver, only while pending. |
| Can an approver apply for leave? | Yes, to their own approver. |
| User without an approver? | Cannot apply (400, button hidden). |
| 45-day window for floating holidays? | Not applicable (Floating is out of scope). |
| Pending request when the cap is hit later? | Not re-evaluated. It stays pending and still counts. |

---

## 17. Process and deliverables

1. **Test-first history.** Every cycle is its own commit: `red:`, `green:` or `refactor:`, with the ZOMBIES tag. Commit the failing test (with the failing output visible) before the implementation. Do not squash. Let Claude Code do this one test at a time: write the test, run it and show the failure, commit `red:`, implement, run, commit `green:`.
2. **Keep this spec current.** The ZOMBIES tables in sections 12 to 14 are the spec for each unit. If a decision changes during the build, update the table and commit it as `docs:`. Mark any rows you skipped and why. How the spec was written: screens, then rules list, then ZOMBIES examples, then tests.
3. **AI_LOG.md.** Keep it as you go, one line per suggestion: what Claude proposed, whether you accepted or rejected it, and why. Write it in your own words. Rejections with reasons matter most. Examples from planning:
   - Slack and email integration: rejected, out of scope.
   - Django templates for the pages: replaced by static HTML shells.
   - React: rejected, you wanted plain TypeScript.
   - Separate `/api/csrf` endpoint: dropped, login sets the cookie.
   - SQLite: replaced by PostgreSQL.
   - Business logic in views: replaced by a service layer.
4. **CLAUDE.md.** Put the layers, naming rules and endpoint table in it so every Claude Code session follows them. Run one task per session and end each with its demo.
5. **Walkthrough (5 to 7 minutes).**
   1. Show the commit history (red, green, refactor with ZOMBIES tags).
   2. Task 1 demo as Ankit.
   3. Task 2 demo as Priya, then back to Ankit. Then Priya applies and Rohan approves.
   4. Task 3 demo as Aarav.
   5. Say what was cut and why.
   6. Describe one suggestion you rejected and what you did instead.
   7. One line: "Backend rules are tested in pytest. Frontend tests cover rendering, escaping and button states."

---

## 18. Order of work

1. Step 0: setup.
2. Task 1, finished end to end and demoed.
3. Task 2, finished end to end and demoed.
4. Task 3, finished end to end and demoed.
5. Review this spec and the AI log, then rehearse the walkthrough.
