# Part 1 · Day 2 — TDD in Python

**Date completed:** YYYY-MM-DD · **Time spent:** ~<hours>

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Follows red-green-refactor without skipping steps | Yes / Partly / No | [section](#red-green-refactor) |
| Chooses the next test using ZOMBIES | Yes / Partly / No | [section](#zombies) |
| Uses pytest fixtures and parametrize | Yes / Partly / No | [code](../code/part-1/day-02-notification-service/) · [section](#pytest-essentials) |
| Builds a service test-first | Yes / Partly / No | [code](../code/part-1/day-02-notification-service/) · [section](#exercise-1-notification-service-test-first) |
| Shows the TDD cycle in commit history | Yes / Partly / No | [section](#exercise-2-commit-after-every-green-and-refactor-step) |
| Extends the design without breaking existing tests | Yes / Partly / No | [section](#exercise-3-add-a-new-channel-without-changing-existing-tests) |

## Key learnings

### The Three Laws of TDD

<2–3 lines>

### Red-green-refactor

<2–3 lines: the cycle and why the test comes first>

### ZOMBIES

<2–3 lines: how it helps pick the next test>

### pytest essentials

<2–3 lines: test functions, assertions, fixtures, parametrize>

## Exercises

### Exercise 1: Notification service test-first

<What the service does, the one interface for email and SMS, how to run it: [README](../code/part-1/day-02-notification-service/README.md)>

| # | Test | ZOMBIES |
| --- | --- | --- |
| 1 | <test name> | <Z / O / M / B / I / E / S> |

```
$ pytest -v
<paste output>
```

### Exercise 2: Commit after every green and refactor step

```
$ git log --oneline -- code/part-1/day-02-notification-service
<paste output>
```

### Exercise 3: Add a new channel without changing existing tests

<Which channel you added and how>

```
$ git diff <before>..<after> -- code/part-1/day-02-notification-service/tests
<paste output showing only additions>
```

## Reflection

<3–6 sentences: where did writing the test first change your design?>

## AI use

- <tool: what you used it for>
- **What I corrected:** <...>

## Open questions

- <...>

## Changes after review

- None yet.
