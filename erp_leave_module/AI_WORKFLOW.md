# AI Workflow Note

> **Status: draft for the planning phase.** Written from the planning conversation with Claude, in first person so it can be submitted as my own note. I need to read it, correct anything that doesn't match what I actually decided, and put it in my own words. Items marked *(implicit)* were kept in the plan without me giving an explicit yes. Build-phase entries (Tasks 1 to 3) are filled in at the end, from the "AI log candidates" Claude Code prints at each checkpoint.

## 1. How I used Claude

| Phase | Tool | What I used it for |
|---|---|---|
| Planning (done) | Claude chat | Turn five screens into scope, rules, tests, endpoints, and the docs `SPEC.md`, `CLAUDE.md`, `DEVELOPER_GUIDE.md` |
| Build (next) | Claude Code | Write tests and code step by step from `DEVELOPER_GUIDE.md`, one red/green commit at a time |
| Wrap-up | Me | Final `SPEC.md` review, this note, the walkthrough |

I treated Claude's output as a proposal. I pushed back with questions whenever something looked unnecessary (templates, a CSRF endpoint, TypeScript, serializer logic) and changed direction when the answer didn't convince me.

## 2. How the spec was written

1. **Read the rules off the screens.** I gave Claude five screenshots (apply, probation block, floating holiday, approvals, My leaves). Claude listed the rules they imply: working days only, half-day on a single date, overlap, read-only approver, reject needs a comment, 2 days a month on probation. Aarav's screen gave a ready-made test case (1.5 used, 2-day request, 1.5 over).
2. **I cut the scope.** From Claude's longer list I kept only: apply for Personal leave, approvals, the probation cap, plus a simple My leaves landing page. Floating, Leave without pay, withdraw/cancel, Slack and email were cut.
3. **Write down the gaps the screens leave open.** Claude listed ambiguities and proposed a call for each. These are in `SPEC.md` section 16 (for example: pending and approved count toward the cap, rejected doesn't; a request spanning two months is checked per month; the cap covers Personal only because Leave without pay is out of scope).
4. **Plan the tests with ZOMBIES.** I asked for ZOMBIES (Zero, One, Many, Boundaries, Interfaces, Exceptions). Claude produced a table per unit: working days, overlap, the leaves API, decisions, the probation check, and the frontend.
5. **Name every test as a sentence,** then map each to a ZOMBIES tag. The tag goes in the commit message, not the test name.
6. **Consolidate** into `SPEC.md` (what, with the ZOMBIES tables), `DEVELOPER_GUIDE.md` (how, step by step) and `CLAUDE.md` (standing rules).
7. **During the build:** before each unit's tests, Claude Code reads that unit's ZOMBIES table in `SPEC.md` and updates it, with a `docs:` commit, if a row changes. I review those changes.

Method in one line: screens → rules list → decisions on gaps → ZOMBIES examples → named tests → one `SPEC.md`.

## 3. Decisions I made that changed Claude's plan

| My decision | Effect |
|---|---|
| Only apply, approvals, probation cap, and a simple My leaves page | Dropped Floating, LWP, withdraw/cancel, notifications, filters, tabs |
| Real login page (email and password only) | Replaced Claude's seeded user switcher |
| Three sprint tasks, each end to end before the next | Task 1 apply, Task 2 approvals, Task 3 probation |
| Django backend, plain TypeScript frontend, no React | Replaced Claude's default stack (Express, SQLite, React) |
| Asked why Django serves the HTML, and why TypeScript | Templates replaced by static HTML shells plus `/api/me`. I kept TypeScript for typed API contracts. |
| Follow ZOMBIES | Test lists reordered and expanded |
| Approvers can also apply, with a fourth user (Rohan). An approver can't be their own approver. | Added Rohan, a database constraint, and a "no approver means can't apply" rule |
| Return the `/api/me` data from login, and asked what the CSRF endpoint is for | Login returns the same payload as `/api/me`. The `/api/csrf` endpoint was dropped. |
| Use DRF and a proper service layer | Rules, services, serializers and views split into layers |
| Clear names for tests, views and serializers | Naming rules table; rules functions, views and serializers renamed |
| PostgreSQL | Replaced SQLite |
| Remove the time estimate from the plan | Section removed |

## 4. Claude's suggestions I accepted

| Suggestion | Why I kept it |
|---|---|
| Three tasks, each with its own demo | Matches the sprint-style build I wanted |
| Pure `rules.py` with no Django or DB | Fast tests, and the core logic is easy to explain |
| Working-day and cap logic only in Python, with the Apply page calling a preview endpoint | One source of truth, half the tests |
| An `escapeHtml` helper and a test for it | Plain TypeScript rendering is where XSS slips in |
| Vitest with jsdom, a pure `renderX` plus `initX` split, and testing only rendering, escaping and button states | Small, fast frontend tests with no duplicate rule logic |
| Parametrizing Boundary and Many cases | Fewer test functions without dropping cases |
| `is_approver` derived from the data, not a stored flag | One less field that can drift out of sync |
| A database `CheckConstraint` so a user can't approve themselves | Enforced by Postgres, not just the UI |
| Dropping `/api/csrf` (login sets the cookie, `/api/me` is the fallback) | Fewer endpoints, same safety |
| Domain exceptions plus one handler that maps them to 400, 403, 404, 409 | Keeps views thin |
| A 401 subclass of `SessionAuthentication` | DRF returns 403 for anonymous users by default |
| The cap covers Personal only; pending and approved count; per-month split | Sensible calls on gaps in the screens *(implicit, I was asked to confirm and didn't object)* |
| Services take a `today` argument | Seeded 2026 data keeps passing in later years |
| Commit prefixes `red:`, `green:`, `refactor:` with the ZOMBIES tag; stubs before the first red; `test:` commit for a test that already passes | Honest history instead of faked failures |
| `CLAUDE.md` plus a step-by-step `DEVELOPER_GUIDE.md` | So Claude Code follows the same rules every session |

## 5. Claude's suggestions I rejected or changed

| Suggestion | What happened |
|---|---|
| Express, SQLite and React as the default stack | Rejected. Django, DRF, PostgreSQL, plain TypeScript. |
| A seeded user switcher instead of real auth | Rejected. A login page. |
| Stubbing the notifier (fake Slack and email), floating selection, cancel and withdraw | Rejected. Cut from scope entirely. |
| Django templates for the pages, and a `/api/csrf` endpoint | Rejected after my questions. Claude agreed the templates were a habit and the endpoint was avoidable. |
| `JsonResponse` views with no DRF | Replaced. I'm more comfortable with DRF. |
| Logic in thin views | Replaced with a service layer. |
| An optional Playwright smoke test at the end | Not adopted. The plan stays with pytest and Vitest. |
| An optional "x of 2 days used" line on My leaves for probation users | Left as optional. The build guide says skip it unless I ask. |
| Trimming to about 60 to 70 tests | Partly adopted. I took the parametrizing, but the list grew to 90 after I added the service layer and the approver chain, and I kept the half-day-on-a-weekend case. |
| A time estimate in the plan document | Rejected. I had it removed. |

## 6. Mistakes Claude made that I or Claude corrected

- **Christmas example.** The first Task 1 list said Thu 24 to Mon 28 Dec was 3 days and left a "check your calendar" note. With Christmas skipped it is 2, which matches the My leaves screen. Claude corrected it and split it into a 3-day test (no holidays) and a 2-day test (with Christmas).
- **ZOMBIES started at One.** The first test was "single weekday = 1". ZOMBIES starts at Zero, so the first red test became a Sunday counting 0.
- **Test count undercounted.** Claude said about 45 backend and 15 frontend tests, then recounted to about 100 from its own tables. After trimming and later changes the plan stands at 90.
- **Vague test name.** I asked what `test_breakdown_labels_weekends_and_holidays` meant. Claude explained it and renamed it to a clearer sentence.

## 7. Open items

- **Blank reason on submit:** currently checked in the serializer as format validation. Claude offered to move it into `submit_leave` with its own exception. I haven't decided.
- **Probation line on My leaves:** still optional.

## 8. What I checked and what I didn't

- The plan documents were read against the five screens. Dates in the examples were checked against the calendar shown on the screens (for example, Mon 23 Nov and Thu 24 Dec 2026).
- **No code has been run yet.** Test counts in the plan are planned counts. Parametrized tests will expand into more pytest cases.

## 9. Build-phase log (fill in at each checkpoint)

| Task | Claude Code suggestion | Accepted or rejected | Why |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

Also list here any test that passed immediately (committed as `test:`), and any place where I changed the plan during the build.
