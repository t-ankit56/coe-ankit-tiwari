# Part 1 · Day 6 — TypeScript in Practice

**Date completed:** 2026-11-16 · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Writes async TypeScript with promises and async and await | | [fetchUser](../code/part-1/day-06-typescript-user-api/src/api/user-api.ts) |
| Uses narrowing and type guards on external data | | [isUser](../code/part-1/day-06-typescript-user-api/src/guards/is-user.ts) |
| Treats API responses as unknown until checked | | [README](../code/part-1/day-06-typescript-user-api/README.md#decisions) |
| Uses npm scripts for build and test | | [package.json](../code/part-1/day-06-typescript-user-api/package.json) |
| Tests async code with Vitest and test doubles | | [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts) · [fake-fetch.ts](../code/part-1/day-06-typescript-user-api/tests/support/fake-fetch.ts) |
| Builds a typed API module test-first | | [SPEC.md](../code/part-1/day-06-typescript-user-api/SPEC.md) · git log |
| Covers failure and missing-field cases | | [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts) |

## Key learnings

_To write: promises and async/await vs asyncio · narrowing and type guards · why `unknown` · npm scripts · testing async with a test double._

## Exercises

### Exercise 1: Typed user fetcher, test-first

Spec: [SPEC.md](../code/part-1/day-06-typescript-user-api/SPEC.md) · Code and decisions: [README](../code/part-1/day-06-typescript-user-api/README.md) · Design notes: [NOTES.md](../code/part-1/day-06-typescript-user-api/NOTES.md)

_To write: summary of the cycles._

### Exercise 2: Failed request and missing-field tests

Tests for HTTP 404, a rejected fetch, a missing `email` and nine other bad shapes. See [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts).

### Exercise 3: One npm script for typecheck and tests

`npm run check` runs `tsc --noEmit && vitest run`. See [package.json](../code/part-1/day-06-typescript-user-api/package.json).

## Reflection

_To write (yours): where did the type checker catch a mistake that Python would only show at runtime?_

## AI use

_To write (yours)._

## Open questions

-
