# CLAUDE.md

Leave management app. Django REST Framework backend in `backend/`, plain TypeScript frontend in `frontend/`, PostgreSQL. Built test-first in three sprint tasks.

## Read these first

| File | What it is |
|---|---|
| `SPEC.md` | What we are building: scope, users, rules, endpoints, and every test by name in ZOMBIES tables. Source of truth for behaviour. |
| `DEVELOPER_GUIDE.md` | How to build it: contracts, exact steps, commit messages. Follow it in order. |

If these files disagree, `SPEC.md` wins on behaviour and `DEVELOPER_GUIDE.md` wins on process. If something is missing or unclear, stop and ask. Do not invent behaviour.

## Commands

Two folders: `backend/` (Django) and `frontend/` (TypeScript). Run each command from its folder.

```
# backend/   (activate .venv first)
python manage.py runserver          # JSON API on port 8000, no pages
python manage.py migrate
python manage.py seed               # idempotent. `--reset` wipes and reseeds.
pytest                              # all backend tests
pytest leaves/tests/test_rules_working_days.py -x   # one file, stop at first failure

# frontend/
npm run dev                         # Vite on port 5173: serves the pages, forwards /api to Django
npm test                            # vitest (jsdom)
npm run typecheck                   # tsc --noEmit
```

Open the app at http://localhost:5173/login, not port 8000. Both servers must be running.

## Architecture (strict layering)

```
views -> services -> rules
   \-> serializers
```

| Layer | File(s) | Does | Never does |
|---|---|---|---|
| rules | `backend/leaves/rules.py` | Pure calculations (working days, overlap, probation cap) | Import Django, touch the DB, read the clock |
| services | `backend/leaves/services/*.py` | Load data, call rules, write, raise domain exceptions | Know about HTTP, `request`, or `Response` |
| serializers | `backend/leaves/serializers.py` | Field types, required fields, non-blank text, date format | Hold business rules |
| views | `backend/leaves/views.py` | Authenticate, validate input, call one service, serialize output | Contain `if` logic about leave |
| exception handler | `backend/leaves/exception_handler.py` | Map domain exceptions to HTTP status and `{"error": "..."}` | Anything else |

- Services that need "today" take a `today: date | None = None` argument. Never call `date.today()` inside rules.
- Domain errors are exceptions from `backend/leaves/exceptions.py`. Never return error codes or `None` for failure.
- Working-day and probation logic lives only in Python. The frontend calls `GET /api/leaves/preview`. Never reimplement it in TypeScript.
- Use `Decimal` for days, never `float`.
- API fields are `start_date` and `end_date` (not `from`/`to`). Dates are ISO strings (`2026-11-19`). Errors are `{"error": "message"}`.
- Do not use Django templates. Django serves JSON only. The pages are plain HTML files in `frontend/`.

## Naming (readable by someone who has never seen the code)

| Thing | Rule | Example |
|---|---|---|
| Test | `test_<situation>_<outcome>`, a full sentence, no abbreviations, no ZOMBIES tag | `test_rejecting_without_a_comment_is_refused` |
| Test file | `test_<layer>_<unit>.py` | `test_service_approvals.py` |
| View | `<Noun><Action>View` | `ApproveLeaveView` |
| Input serializer | ends in `InputSerializer` | `LeaveSubmissionInputSerializer` |
| Output serializer | ends in `Serializer` | `LeaveRequestSerializer` |
| Service function | `verb_noun` | `submit_leave` |
| Rules function | says what it computes | `count_working_days` |
| Exception | says what went wrong | `LeaveOverlapsExistingLeave` |
| Frontend test | `describe` + `it` sentences | `reject button › stays disabled until the comment has real text` |

Do not abbreviate (`req`, `usr`, `cfg`). Prefer a long clear name over a short vague one.

## Test-first protocol (this is graded, follow it exactly)

Use ZOMBIES order for each unit: **Z**ero, **O**ne, **M**any, **B**oundaries, **I**nterfaces, **E**xceptions.

For every test, in this order:

1. Write **one** test (a parametrized test counts as one).
2. Run it. Confirm it fails, and fails for the right reason (an assertion or `NotImplementedError`, not a typo or import error).
3. Commit only the test: `red: [Z1] a single Sunday counts as zero days`
4. Write the **simplest** code that passes. Hardcoding is fine for Zero and One. Let later tests force generalisation.
5. Run the full relevant suite. Everything must be green.
6. Commit: `green: [Z1] a single Sunday counts as zero days`
7. After a group of cycles, `refactor:` commits change structure only. Tests stay green and no new behaviour is added.

Rules:
- The commit message is `red:`/`green:`/`refactor:`, then the ZOMBIES tag in brackets, then the test name in plain words.
- One test per red/green pair. Never batch several tests into one commit. Never squash. Never amend a pushed commit.
- Never write production code before a failing test requires it.
- If a new test **passes immediately** (earlier code already covers it), do not fake a failure. Commit it as `test: [B2] <name> (already passing, covered by <earlier test>)` and say so in your report.
- Before the first red test of a unit, make one `chore: stub <unit>` commit with functions that raise `NotImplementedError`, so red tests fail on behaviour and not on imports.
- Before the tests of a unit, read that unit's ZOMBIES table in `SPEC.md`. If you add, change or skip a row, update the table and commit it (`docs: update spec for <unit>`).
- Rules tests have no `django_db` mark and never touch the DB. Service and API tests use `@pytest.mark.django_db`.
- Test each business rule once, at the rules or service level. API tests check status codes, response shape and auth only.

## Frontend rules

- Plain TypeScript in `frontend/src/`. No React, no framework. Vite is only the dev server: it serves the pages and forwards `/api` to Django on port 8000.
- Relative imports use the `.js` extension: `import { drawNav } from "./nav.js"`.
- The page markup is written in full in the `.html` files. The shared sidebar is `frontend/partials/sidebar.html`, pulled in with `<!-- include: partials/sidebar.html -->` (a small Vite plugin, `src/partials.ts`).
- Each page file has an `initX()` that fetches data, fills the page and wires events. Fill functions (`fillLeavesTable`, `showPreview`) write into the existing DOM.
- Permissions and state are shown with the `hidden` attribute (for example `#nav-apply.hidden = me.approver === null`). Do not build the page as an HTML string.
- Repeating parts (table rows, list items, day rows) are a `<template>` in the page, copied with `cloneNode(true)`.
- All user text (reason, rejection comment, names) goes in with `textContent`. Never put it in `innerHTML`.
- Tests load the real page with `loadPage("apply")` (`src/__tests__/loadPage.ts`) and assert on the DOM. A hidden element still has `textContent`, so check `hidden`, not text, to see what is shown.
- `api.ts` is the only place that calls `fetch`. It sends `X-CSRFToken` on every POST and redirects to `/login` on 401.
- Every page except login calls `GET /api/me` first. The login page uses the login response and does not call `/api/me`.
- Styling: one plain `styles.css` with a few CSS variables. Do not spend time on polish.

## Do not

- Add features outside `SPEC.md` scope (Floating, Leave without pay, withdraw, cancel, Slack, email, filters, tabs).
- Add libraries beyond the ones in `DEVELOPER_GUIDE.md` without asking.
- Put business logic in views, serializers, models' `save()`, or TypeScript.
- Use `float` for days, `from` as a field name, or Django templates.
- Skip, delete or weaken a test to make something pass.
- Commit `.env`, `node_modules`, `.venv`, or compiled JS.
- Write or edit `AI_LOG.md`. That file is the human's account in their own words.

## Working agreement

- Follow `DEVELOPER_GUIDE.md` step by step. Do not start a step before the previous step's **Verify** passes.
- Stop at every **CHECKPOINT** and report: what was built, test counts (`pytest` and `npm test` summaries), anything that passed immediately, any deviation from the plan.
- At the end of each task, print a short list titled **"AI log candidates"**: suggestions you made that the human accepted or rejected during the task, and any decision the human made that changed the plan. The human will write these up themselves.
- When something in the plan is ambiguous, list the options, give your recommendation in one line, and ask. Do not guess silently.
- Keep summaries short. Name files and commands exactly.

## Seeded data (for manual checks)

Password for everyone: `password123`.

| Email | Role |
|---|---|
| ankit@incubyte.co | Employee, approver Priya |
| aarav@incubyte.co | Employee on probation, approver Priya |
| priya@incubyte.co | Approver for Ankit and Aarav, her approver is Rohan |
| rohan@incubyte.co | Approves for Priya, no approver, cannot apply |
