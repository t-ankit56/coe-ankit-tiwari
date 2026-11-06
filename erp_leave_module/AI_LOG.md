# AI Log

> **Draft written by Claude from the planning and build sessions, at my request.** `CLAUDE.md` says this file is my own account, so I need to read it, correct anything that is wrong, and put it in my own words before submitting. *(implicit)* means Claude proposed it and I never said yes or no, so it stayed in the plan.

One line per suggestion. Rejections matter most.

## Planning (Claude chat)

| # | Claude proposed | Decision | Why |
|---|---|---|---|
| 1 | Express, SQLite and React as the stack | Rejected | I wanted Django, DRF, PostgreSQL and plain TypeScript. |
| 2 | A seeded user switcher instead of real login | Rejected | I wanted a real login page. |
| 3 | A fake notifier (Slack, email), Floating holidays, cancel and withdraw | Rejected | Cut from scope. |
| 4 | Django templates for the pages | Rejected | I asked why. Claude agreed it was a habit. Static HTML shells instead. |
| 5 | A separate `/api/csrf` endpoint | Rejected | I asked what it was for. Login sets the cookie, `/api/me` is the fallback. |
| 6 | `JsonResponse` views with no DRF | Replaced | I am more comfortable with DRF. |
| 7 | Business logic inside thin views | Replaced | I wanted a service layer. |
| 8 | An optional Playwright smoke test | Rejected | Plan stays with pytest and Vitest. |
| 9 | Trimming to 60-70 tests | Partly accepted | I took the parametrizing. The list grew to 90 with the service layer and the approver chain. |
| 10 | A time estimate in the plan | Rejected | I had it removed. |
| 11 | Pure `rules.py`, with working-day and cap logic only in Python (the Apply page calls a preview endpoint) | Accepted | Fast tests, one source of truth. |
| 12 | Derived `is_approver`, and a database `CheckConstraint` so nobody approves themselves | Accepted | One less field to drift, enforced by Postgres. |
| 13 | Domain exceptions plus one handler mapping to 400, 403, 404, 409 | Accepted | Keeps views thin. |
| 14 | A `SessionAuthentication` subclass so anonymous users get 401, not 403 | Accepted | DRF's default is 403. |
| 15 | `escapeHtml` with its own test; Vitest with a pure `renderX` and `initX` split | Accepted | Plain TypeScript rendering is where XSS slips in. |
| 16 | Services take a `today` argument | Accepted *(implicit)* | Seeded 2026 data keeps passing later. |
| 17 | Cap covers Personal only; pending and approved count; per-month split | Accepted *(implicit)* | Sensible calls on gaps in the screens. |
| 18 | `red:`, `green:`, `refactor:` commits with a ZOMBIES tag; stubs first; `test:` for tests that already pass | Accepted | Honest history instead of faked failures. |

## Build (Claude Code)

| # | Task | Claude proposed | Decision | Why |
|---|---|---|---|---|
| 19 | Setup | `git init` inside `erp_leave_module`, as the guide says | Changed | I chose a new branch in the COE repo instead. |
| 20 | Setup | I install Node and the Postgres role myself | Accepted | Claude could not do either from the session. |
| 21 | 1 | Add service row I2 (preview reports overlap) and a nav test for Apply shown when an approver exists | Accepted *(implicit)* | The spec had no row for either behaviour. Both are in `SPEC.md` with `docs:` commits. |
| 22 | 1 | Keep the login serializer minimal at O1 so I1 forces the extra fields | Accepted *(implicit)* | Keeps the tests honest. |
| 23 | 1 | Write page glue (login form, init functions, submit rules) as one untested `feat:` commit | Accepted *(implicit)* | The spec's frontend tables do not cover it. |
| 24 | After 1 | Plain CSS, as `SPEC.md` says | Rejected | I asked to use the UI in `screens/`. Claude restyled to match the HTML mockups. |
| 25 | After 1 | Leave out Floating, Leave without pay, filters, tabs, Withdraw and Cancel, Slack text and the other menus from the mockups | Accepted *(implicit)* | Out of scope in `SPEC.md`. |
| 26 | After 1 | Add a logout link and a 204 test | Accepted *(implicit)* | Needed to switch users in the demo. |
| 27 | 2 | Add rows Z3, E3 (reject has its own not-found and assigned-approver checks) and API I2 (waiting list shape) | Accepted *(implicit)* | E1's first fix only covered approve. |
| 28 | 2 | Let the reject serializer accept blank text so the service raises `CommentRequiredToReject` | Accepted *(implicit)* | The rule has one home, in the service. |
| 29 | 3 | Extract one month-usage helper in its own `refactor:` commit before the suggestion test | Accepted *(implicit)* | The suggestion function must not recurse into `check_probation_limit`. |
| 30 | 3 | Add API row I2 (serialized probation shape) | Accepted *(implicit)* | Nothing else tested that shape. |
| 31 | 3 | Replace the day list with the warning and limit cards when over the cap | Accepted *(implicit)* | That is what the probation screen shows. |
| 32 | 3 | Skip the optional "x of 2 days used this month" line on My leaves | Not built | The guide says skip unless I ask, and I did not. |

## Things that went wrong

- Task 1: a `green:` commit was made with a failing suite. Claude reset it (unpushed), fixed the code, and added a gate that refuses `green:` or `refactor:` unless the suite passes.
- Task 2: one `red:` commit held two tests, and another failed on a syntax error instead of an assertion. Both were reset and redone as single-test cycles.
- Task 2: `reject_leave` first skipped the assigned-approver check. Row E3 was added to cover it.
- After Task 1: form fields on the Apply page were stretched about 200px tall by a flex rule. I reported the gaps and Claude fixed it.
- Planning: the first Christmas example was wrong, ZOMBIES started at One instead of Zero, the first test count was too low, and one test name was vague. All corrected.

## Tests that passed immediately

28 `test:` commits in `git log`, each says which earlier code covered it.
