# Part 1 · Day 6 — TypeScript in Practice

**Date completed:** 2026-11-16 · **Time spent:** ~6 hours

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Writes async TypeScript with promises and async and await | Yes | [fetchUser](../code/part-1/day-06-typescript-user-api/src/api/user-api.ts) |
| Uses narrowing and type guards on external data | Yes | [isUser](../code/part-1/day-06-typescript-user-api/src/guards/is-user.ts) |
| Treats API responses as unknown until checked | Yes | [README](../code/part-1/day-06-typescript-user-api/README.md#decisions) |
| Uses npm scripts for build and test | Yes | [package.json](../code/part-1/day-06-typescript-user-api/package.json) |
| Tests async code with Vitest and test doubles | Yes | [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts) · [fake-fetch.ts](../code/part-1/day-06-typescript-user-api/tests/support/fake-fetch.ts) |
| Builds a typed API module test-first | Yes | [SPEC.md](../code/part-1/day-06-typescript-user-api/SPEC.md) · git log |
| Covers failure and missing-field cases | Yes | [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts) |

## Key learnings

### Promises and async/await

A promise is a value that is not ready yet. It is pending, then fulfilled with a value or rejected with an error. `async` makes a function always return a promise, so `fetchUser` returns `Promise<User>`, and `await` pauses only that function until the promise settles. A `throw` inside an async function rejects the promise, and `await` on a rejected promise throws again, so a normal `try`/`catch` works. It is close to Python's `async def` and `await`, but one difference is that a JavaScript promise starts running as soon as the function is called, while a Python coroutine does nothing until it is awaited.

### Narrowing and type guards

External data has no type I can trust, so I check it before using it. `typeof` and `in` narrow a value inside an `if`. A type guard like `isUser(value: unknown): value is User` packs those checks into one function, and when it returns true the compiler treats the value as a `User`. `typeof null` is `"object"`, so the guard needs an `isObject` helper that rules out `null` first, or `"id" in null` crashes.

### Why `unknown`

`response.json()` is typed `Promise<any>`, and `any` turns the checker off. I assign it to `unknown`, which cannot be used until it is narrowed, so the guard is the only way to get a `User`. I never use `as User`, because a cast tells the compiler to believe me without checking anything. The compiler also trusts the guard completely, so the tests are the only protection if the guard is wrong. That is why I grew it one field at a time, with a test for each.

### npm scripts

`package.json` holds the commands: `test` runs Vitest, `typecheck` runs `tsc --noEmit`, `check` runs both, and `build` compiles `src/`. `npm test` does not type-check, because Vitest strips the types and runs the code, so a file with a type error still passes. I run `check`, not just `test`.

### Testing async code with a test double

`fetchUser` takes the fetch function as a parameter, so the tests pass a small hand-written `fakeFetch` that returns a chosen body and status and records the URLs. There is no mocking library and no network. A rejected promise is tested with `await expect(promise).rejects.toThrow("text")`, and `it.each` covers nine bad shapes with readable names. `fetch` only rejects on a network failure, so a 404 is a normal response and I check `response.ok` myself.

## Exercises

### Exercise 1: Typed user fetcher, test-first

Spec: [SPEC.md](../code/part-1/day-06-typescript-user-api/SPEC.md) · Code and decisions: [README](../code/part-1/day-06-typescript-user-api/README.md) · Design notes: [NOTES.md](../code/part-1/day-06-typescript-user-api/NOTES.md)

Six red-green-refactor cycles, one commit per step. The cycle table is in the [README](../code/part-1/day-06-typescript-user-api/README.md#cycles).

- **Cycle 1 (Zero):** a valid response returns the user. The body is read as `unknown` and only `isUser` turns it into a `User`.
- **Cycle 2 (One):** the request URL contains the id.
- **Cycles 3 and 4 (Boundary):** a missing `email` is rejected, then the guard checks every field and its type, with nine bad shapes in one `it.each`.
- **Cycle 5 (Exceptional):** a 404 rejects with the status, and a network error rejects with context and the original error as `cause`.
- **Cycle 6 (Refactor):** no behaviour change, only the public exports and a corrected doc comment.

14 tests, no network, and a hand-written `fakeFetch` passed in as a parameter. I checked the real API by hand once, for ids 1 and 9999.

### Exercise 2: Failed request and missing-field tests

Tests for HTTP 404, a rejected fetch, a missing `email` and nine other bad shapes. See [user-api.test.ts](../code/part-1/day-06-typescript-user-api/tests/api/user-api.test.ts).

### Exercise 3: One npm script for typecheck and tests

`npm run check` runs `tsc --noEmit && vitest run`. See [package.json](../code/part-1/day-06-typescript-user-api/package.json).

## Reflection

Python shows the wrong type when a line is run but in typescript wrong type is shown during compilation time. In this project it was visible in the response I got from the public api. In python it would have been stored as dictionary and would raise an error when run. But in typescript we take the input as unknown type and we have to prove that it belongs to a type before running the program.

## AI use

- **Claude Code:** wrote the spec ([SPEC.md](../code/part-1/day-06-typescript-user-api/SPEC.md)), then built the module with me one cycle at a time. Each cycle started in plan mode, I approved the plan, and Claude stopped after every red, green and refactor step so I could commit. I made every commit. It also wrote the project README and `NOTES.md`, and explained async/await, type guards, `unknown` and Vitest.
- **I decided:** to take the fetch function as a parameter, to use `unknown` and a hand-written guard instead of zod, to reject the promise instead of returning a `Result`, to split `src` by role, and to wrap network errors with `cause`.
- **What I corrected:** the first version was built all at once, so I had it reset and rebuilt one cycle at a time. Claude's first spec also hardcoded the return value in the early cycles. We removed those steps so cycle 1 writes the real path.


## Open questions

-
