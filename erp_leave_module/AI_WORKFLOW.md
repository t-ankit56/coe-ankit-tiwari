# AI Workflow Note

> **Draft written by Claude from the sessions, at my request.** I need to read it, correct anything that does not match what I decided, and put it in my own words. The full one-line-per-suggestion list is in `AI_LOG.md`.

## 1. How I used Claude

| Phase | Tool | Used for |
|---|---|---|
| Planning | Claude chat | Turn five screens into scope, rules, tests and the three docs: `SPEC.md`, `CLAUDE.md`, `DEVELOPER_GUIDE.md` |
| Build | Claude Code | Write tests and code from `DEVELOPER_GUIDE.md`, one red/green commit at a time, with a stop at each checkpoint |
| Wrap-up | Me, with Claude | Spec review against the code, README, this note |

I treated Claude's output as a proposal. I pushed back with questions when something looked unnecessary (templates, a CSRF endpoint, TypeScript, serializer logic) and changed direction when the answer did not convince me.

## 2. How the spec was written

1. **Rules from the screens.** Claude read five screenshots and listed the rules they imply: working days only, half day on a single date, overlap, read-only approver, reject needs a comment, 2 days a month on probation. Aarav's screen gave a ready-made test (1.5 used, 2 requested, 1.5 over).
2. **I cut the scope** to apply, approvals, the probation cap and a simple My leaves page. Floating, Leave without pay, withdraw, cancel and notifications were cut.
3. **Gaps written down.** Claude listed what the screens leave open and proposed a call for each. They are in `SPEC.md` section 16.
4. **ZOMBIES tables.** I asked for ZOMBIES (Zero, One, Many, Boundaries, Interfaces, Exceptions). Claude drafted a table per unit and I named every test as a sentence. The tag goes in the commit message, not the test name.
5. **Three files.** `SPEC.md` is what and which tests, `DEVELOPER_GUIDE.md` is how step by step, `CLAUDE.md` is the standing rules.
6. **Kept current during the build.** Claude read each unit's table before writing its tests and committed a `docs:` change when a row changed. Seven rows were added and none were dropped. See `SPEC.md` section 15.

Method in one line: screens, rules list, decisions on gaps, ZOMBIES examples, named tests, one `SPEC.md`.

## 3. Suggestions I accepted

- Three tasks, each end to end with its own demo.
- A pure `rules.py` (no Django, no database), with working-day and cap logic only in Python and a preview endpoint for the UI.
- A service layer, domain exceptions and one handler that maps them to 400, 403, 404 and 409.
- A database constraint so nobody approves their own request, and `is_approver` derived from the data.
- `escapeHtml`, and Vitest tests for rendering, escaping and button states only.
- `red:`, `green:`, `refactor:` commits with ZOMBIES tags, stubs before the first red, and `test:` commits when a test already passes.
- During the build, Claude proposed seven extra spec rows where behaviour had no test (preview overlap, Apply link, reject's own 404 and 403, waiting list shape, probation shape, 204 on logout). They stayed in.

## 4. Suggestions I rejected or changed

- Express, SQLite and React as the stack: replaced by Django, DRF, PostgreSQL and plain TypeScript.
- A seeded user switcher: replaced by a real login page.
- Django templates and a `/api/csrf` endpoint: dropped after my questions. Static HTML shells instead, and login sets the cookie.
- A fake Slack and email notifier, Floating holidays, cancel and withdraw: cut from scope.
- `JsonResponse` views with no DRF, and logic in views: replaced by DRF and the service layer.
- An optional Playwright test, a time estimate, and trimming to 60-70 tests: not adopted.
- After the build: I asked to split the app into `backend/` and `frontend/` folders in the same repo, running locally. Claude proposed a Vite dev server with a proxy instead of CORS, and I accepted it. This replaced the "no bundler" rule.
- During the build: I used a new branch in the COE repo instead of `git init` in the module, and I asked for the UI from `screens/` instead of plain CSS. Claude left out what those mockups show beyond scope (Floating, filters, tabs, Slack text, other menus).

## 5. Mistakes that were caught

- A `green:` commit with a failing suite, a `red:` commit holding two tests, and a `red:` commit that failed on a syntax error. Each was reset before pushing and redone. Claude added a gate that refuses `green:` or `refactor:` unless the suite passes.
- The reject endpoint first skipped the assigned-approver check. A new row (E3) now covers it.
- In the split, a commit picked up compiled `.js` files after an ignore rule stopped matching, and Claude's first proxy plan assumed the wrong Host header, so POSTs failed with 403 until the dev origin was trusted. Both were found by checking, and fixed.
- A CSS rule stretched the Apply form fields about 200px tall. I reported it and it was fixed.
- In planning: a wrong Christmas example, ZOMBIES starting at One, a low test count, and a vague test name.

## 6. What I checked and what I did not

- `pytest` (92 cases from 83 test functions), `npm test` (16) and `npm run build` pass. A fresh clone following only `README.md` passes too.
- Every test name in the `SPEC.md` tables exists in code, and every red commit has a matching green (71 pairs). 28 `test:` commits mark tests that passed immediately.
- Each task's demo was run against the real server over HTTP with real logins and CSRF tokens.
- **[Fill in what I checked by hand in the browser.]** Claude cannot see a browser, so the page layout was only checked by me.
- Not built: the optional probation line on My leaves, Contact HR, and the Decided tab.

## 7. Open items

- Blank reason on submit is still checked in the serializer as format validation. Claude offered to move it into `submit_leave` with its own exception. I have not decided.
