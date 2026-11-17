# Typed User API Module (Day 6)

`fetchUser(id, fetchFn)` fetches one user from JSONPlaceholder, checks the JSON with a type guard and returns a typed `User`. Built test-first with Vitest. Spec: [SPEC.md](SPEC.md) · Design notes per cycle: [NOTES.md](NOTES.md).

## Run

```bash
npm install
npm test            # Vitest
npm run typecheck   # tsc --noEmit
npm run check       # typecheck and tests together
npm run build       # compiles src/ to dist/
```

## Structure

```
src/
  index.ts           public exports
  models/user.ts     the User type
  guards/is-user.ts  the isUser type guard
  api/user-api.ts    fetchUser and the FetchFn type
tests/
  api/               tests, mirroring src/api
  support/           fake-fetch.ts (test double) and fixtures.ts (sample users)
```

## Design

`fetchUser` builds the URL for the id, calls the fetch function it was given, and checks what comes back before it returns a `User`. The body is read as `unknown`, and only `isUser` can turn it into a `User`. A network error, a bad status or a bad shape makes the returned promise reject.

## Decisions

- **The response is `unknown` until `isUser` passes.** `response.json()` is assigned to `unknown`, and the guard is the only way to get a `User`. There are no `any` and no `as` casts.
- **The fetch function is a parameter.** Tests pass a small fake, so there is no network and no mocking library. The real `fetch` is passed in by the caller.
- **Failures reject the promise.** A non-ok status and a bad shape throw an `Error` inside the async function. A network error from the fetch function is wrapped as `Could not reach the API for user {id}`, with the original error kept as `cause`.
- **The guard checks only the fields we use** (`id`, `name`, `email`, `address.city`). The real response has more (`company`, `geo` and so on). Those extra fields stay on the returned object at runtime but are not in the `User` type.
- **Checked against the real API by hand:** `/users/1` returns a typed user and `/users/9999` rejects with `Request failed with status 404`.

## Cycles

| Cycle | Test | ZOMBIES |
| --- | --- | --- |
| 1 | A valid response returns the user | Zero |
| 2 | The request URL contains the id | One |
| 3 | A response missing `email` is rejected | Boundary |
| 4 | Every field and its type, with nine bad shapes in one `it.each` | Boundary |
| 5 | A 404 is rejected with the status, and a network error is rejected with context | Exceptional |
| 6 | Final cleanup and public exports | Refactor |

14 tests in total.
