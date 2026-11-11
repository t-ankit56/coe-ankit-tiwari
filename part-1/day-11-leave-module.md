# Part 1 · Day 11 — Leave Module

**Date completed: 11-11-2026** · **Time spent: ~20 hours**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Delivers a working vertical slice for apply and approve or reject | | [Exercise](#exercise-the-leave-module) · [README](../erp_leave_module/README.md) |
| Applies one playbook rule as a warning | | [Playbook rule: probation](#playbook-rule-probation-cap) · [SPEC.md, Probation cap](../erp_leave_module/SPEC.md) |
| Builds test-first with red-green-refactor commits | | `git log` on `feature/erp-leave-module` (`red:`, `green:`, `refactor:`) · [CLAUDE.md, Test-first protocol](../erp_leave_module/CLAUDE.md) |
| Writes the spec before the code | | [SPEC.md](../erp_leave_module/SPEC.md) · [DEVELOPER_GUIDE.md](../erp_leave_module/DEVELOPER_GUIDE.md) |
| Records which Claude suggestions were accepted and rejected and why | | [AI_LOG.md](../erp_leave_module/AI_LOG.md) · [AI_WORKFLOW.md](../erp_leave_module/AI_WORKFLOW.md) |
| Gives a live walkthrough of the code and explains the design choices | | Given live, not written here |

## Key learnings

### Playbook rule: probation cap

While an employee is on probation, Personal leave is capped at 2 days per calendar month.

### Writing the spec first

I wrote the spec in Claude chat before any code. Claude read the five screens and listed the rules they imply (working days only, half day on one date, overlap, reject needs a comment, 2 days a month on probation). I cut the scope to apply, approvals, the probation cap and a simple My leaves page, and Claude listed what the screens leave open so I could decide each gap.

I asked for ZOMBIES tables per unit and named every test as a sentence, then kept the spec as three files: [SPEC.md](../erp_leave_module/SPEC.md) (what and which tests), [DEVELOPER_GUIDE.md](../erp_leave_module/DEVELOPER_GUIDE.md) (how, step by step) and [CLAUDE.md](../erp_leave_module/CLAUDE.md) (standing rules). The spec stayed current during the build: seven test rows were added and none dropped.

Full steps, with what I accepted and rejected: [AI_WORKFLOW.md, How the spec was written](../erp_leave_module/AI_WORKFLOW.md).

## Exercise: the leave module

Stack: Django REST Framework, plain TypeScript, PostgreSQL. Spec, setup steps and every test by name are in [SPEC.md](../erp_leave_module/SPEC.md) and [DEVELOPER_GUIDE.md](../erp_leave_module/DEVELOPER_GUIDE.md). Run instructions are in the [README](../erp_leave_module/README.md).

### Evidence

Backend, `pytest` in `erp_leave_module/backend`:

```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.2.0, pluggy-1.7.0
django: version: 5.2.19, settings: config.settings (from ini)
configfile: pytest.ini
testpaths: leaves/tests
plugins: django-4.14.0
collected 92 items

leaves/tests/test_api_approvals.py ...........                           [ 11%]
leaves/tests/test_api_auth.py ......                                     [ 18%]
leaves/tests/test_api_leaves.py ..........                               [ 29%]
leaves/tests/test_seed_command.py .                                      [ 34%]
leaves/tests/test_service_approvals.py .............                     [ 48%]
leaves/tests/test_service_leaves.py .............                        [ 63%]
leaves/tests/test_rules_overlaps.py ......                               [ 69%]
leaves/tests/test_rules_probation.py ............                        [ 82%]
leaves/tests/test_rules_working_days.py ................                 [100%]

============================= 92 passed in 36.77s ==============================
```

Frontend, `npm test` in `erp_leave_module/frontend`:

```
 ✓ src/__tests__/partials.test.ts (1 test) 4ms
 ✓ src/__tests__/login.test.ts (1 test) 13ms
 ✓ src/__tests__/api.test.ts (3 tests) 25ms
 ✓ src/__tests__/nav.test.ts (3 tests) 101ms
 ✓ src/__tests__/approvals.test.ts (2 tests) 100ms
 ✓ src/__tests__/myLeaves.test.ts (3 tests) 104ms
 ✓ src/__tests__/apply.test.ts (3 tests) 343ms

 Test Files  7 passed (7)
      Tests  16 passed (16)
```


## Reflection

### What I would build next

- Show the probation warning to the approver too, so they can see the request went over the limit when they decide. Right now only the employee sees it.
- The approver view should have filters and sorting mechanism to make it easy for approver to review requests.
- Let an employee withdraw a pending request, which I cut from scope.
- Add other leave types (Floating, leave without pay).
- Send the approver and employee a Slack or email message when a request is made or decided.
- Add a second playbook rule such as quorum, to check the rules layer takes a new rule cleanly.

### What I would ask HR or the product owner first

- Who approves when the approver is away or has left, and can approval be delegated?
- Does the cap apply to every leave type, and when does probation end?
- What should happen if an approver is not set for an employee?
- What all roles are required with what level of permissions?

## AI use

Claude drafted [AI_LOG.md](../erp_leave_module/AI_LOG.md) from the planning and build sessions. I need to read it, correct it and put it in my own words before submitting.

Claude also drafted the Reflection section above. I will rewrite it in my own words before submitting.


## Changes after review

- None yet.
