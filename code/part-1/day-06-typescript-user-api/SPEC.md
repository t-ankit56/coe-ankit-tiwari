# Typed User API Module in TypeScript: Build Spec for Claude Code


Build a small module, `fetchUser`, that fetches one user from the public JSONPlaceholder API, checks the shape of the JSON with a type guard, and returns typed data, in TypeScript with Vitest, strictly test-first. This is for the Day 6 assessment, so the order of tests and the commit history matter as much as the final code.

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every cycle, enter plan mode. The plan names the test you will write, the minimal code to pass it, and the refactor you expect. Write no files until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each red, green and refactor step, run `npm test` and `npm run typecheck`, give a suggested commit message, then wait.
3. **Red, green, refactor, never skipped.** Red: write one failing test and run it. Confirm it fails for the expected reason (an assertion, not a typo or an import error). Green: write the least code that makes it pass. Refactor: clean up while all tests stay green. If you find nothing to refactor, say why.
4. **One cycle at a time.** Never write production code before a failing test asks for it. Never write the next test before the current one is green.
5. **Stop after each cycle.** Show the test, the code and the suggested commit messages, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
6. **Simplest real thing first.** Write the smallest real code that passes. Do not hardcode return values, and do not add features no test asks for.
7. **Do not edit an old test to make a new one pass.** The only allowed edit to old tests is a pure refactor of shared setup, such as moving the fake fetch into its own file.
8. **No real network in tests.** `fetchUser` receives the fetch function as a parameter and the tests pass a fake. The only live call is one manual check at the end. Dev dependencies only: `typescript` and `vitest`. No zod or other schema library.
9. **External data is `unknown`.** The parsed JSON is typed `unknown` and becomes a `User` only after the type guard passes. No `any` and no `as User`.
10. **Tests are ordered by ZOMBIES:** Zero, One, then Boundary and Exceptional cases, always keeping scenarios and solutions simple.
11. **Keep notes.** Whenever a test changes the design, append one line to `NOTES.md`. The user will use these for the reflection.
12. **Reflection and AI use are the user's.** Do not write them in the day file.

## Scope

- `fetchUser(id, fetchFn)`, an async function that returns `Promise<User>`
- A `User` interface and an `isUser(value: unknown): value is User` type guard
- A fake fetch function in the tests only
- npm scripts for tests, type checking, both together, and a build

## Design

`fetchUser` knows nothing about the network library. It builds a URL, asks the fetch function it was given, and checks what comes back before it hands out a `User`. A bad status or a bad shape makes the returned promise reject with an `Error`.

| Piece | Job |
| --- | --- |
| `User` | Interface with readonly `id`, `name`, `email` and `address.city`. Only the fields this module uses. |
| `isUser` | Takes `unknown` and checks the object, each field, its type, and the nested `address.city`. |
| `FetchFn` | The part of `fetch` that `fetchUser` needs: a URL in, a response with `ok`, `status` and `json()` out. |
| `fetchUser` | Calls the fetch function, wraps a network error with context, throws on a bad status, reads the body as `unknown`, runs `isUser`, throws if it fails, returns the `User`. |

```ts
interface User {
  readonly id: number;
  readonly name: string;
  readonly email: string;
  readonly address: { readonly city: string };
}

type FetchFn = (url: string) => Promise<{
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
}>;

function isUser(value: unknown): value is User;
function fetchUser(id: number, fetchFn: FetchFn): Promise<User>;
```

**Decisions made up front, so nothing is guessed**

- The API is `https://jsonplaceholder.typicode.com/users/{id}`. Its data is fixed: `/users/1` is always Leanne Graham, and `/users/9999` returns a 404.
- `fetchUser(id: number, fetchFn: FetchFn)`. The caller passes the real `fetch`. Tests pass a fake. There is no default, so nothing reaches the network by accident.
- The request URL is `https://jsonplaceholder.typicode.com/users/${id}`.
- `response.json()` is assigned to a variable typed `unknown`. Only `isUser` can turn it into a `User`.
- `isUser` checks only the fields in `User`. The real response has more (`username`, `company`, `geo`). They are ignored, not rejected.
- A response whose `ok` is false makes `fetchUser` throw `new Error("Request failed with status 404")`, with the real status code.
- A response whose body fails `isUser` makes it throw `new Error("Response is not a valid user")`.
- A fetch function that rejects is caught around that one call only. `fetchUser` throws `new Error("Could not reach the API for user 7")` with the original error as its `cause`, so the caller sees what failed and why.
- In TypeScript a `catch` variable is `unknown`. It is passed on as `cause` without any check, because `cause` accepts `unknown`.
- No retries, no timeout, no logging.

## Folder layout

```
code/part-1/day-06-typescript-user-api/
  package.json
  tsconfig.json
  tsconfig.build.json
  .gitignore
  README.md
  NOTES.md
  SPEC.md
  src/
    index.ts           # public exports
    models/
      user.ts          # User
    guards/
      is-user.ts       # isUser type guard
    api/
      user-api.ts      # FetchFn, fetchUser
  tests/
    api/
      user-api.test.ts # mirrors src/api
    support/
      fake-fetch.ts    # fakeFetch test double
      fixtures.ts      # sample users
```

`src` is split by role: types in `models`, runtime checks in `guards`, the network code in `api`. `tests` mirrors `src`, and shared test helpers live in `tests/support`, so they are never mistaken for tests. `index.ts` is the only file other code should import from.

In the tests, use `fakeFetch(body, status)` from `tests/support/fake-fetch.ts`. It answers every request with the given body and status, and records the URLs it was called with. That keeps the tests independent of the network.

## Step 0: Project setup

Do this before cycle 1. No tests or production code yet.

1. Create the folder and `npm init -y`. Install `typescript` and `vitest` as dev dependencies.
2. Add `tsconfig.json` with `strict: true`, target ES2022, `moduleResolution: bundler`, and `include` of `src` and `tests`. Add `tsconfig.build.json` that extends it, includes only `src`, and sets `noEmit: false`, `outDir: "dist"` and `rootDir: "src"`.
3. Add these scripts:
   - `"test": "vitest run"`
   - `"typecheck": "tsc --noEmit"`
   - `"check": "tsc --noEmit && vitest run"`
   - `"build": "tsc -p tsconfig.build.json"`
4. Add a `.gitignore` with `node_modules/` and `dist`. Create an empty `NOTES.md`.
5. Run `npm test` and confirm it reports "no test files found" (it exits with code 1, which is normal with no tests). `npm run typecheck` fails with `TS18003: No inputs were found` until a `.ts` file exists, and passes once cycle 1 adds files.

**Suggested commit message:** `chore: project skeleton with Vitest, strict tsconfig and npm scripts`

## The tests, in ZOMBIES order

| Tag | Test | Expectation |
| --- | --- | --- |
| Z1 | `returns the user when the response is a valid user` | The resolved value equals the user |
| O1 | `requests the JSONPlaceholder URL for the given id` | The fake saw `.../users/7` once. Passes at once after cycle 1. |
| B1 | `rejects when the response is missing the email field` | Rejects with `Response is not a valid user` |
| B2 | `rejects when %s` | `it.each` over missing or wrong-type fields, a missing `address.city`, `null`, a string and an array |
| E1 | `rejects with the status when the request is not ok` | HTTP 404 rejects with `Request failed with status 404` |
| E2 | `rejects with context and the original error when the fetch itself fails` | Rejects with `Could not reach the API for user 1`, and `cause` is the original error |

## The cycles

Each cycle is red, green, refactor. Start every cycle in plan mode and wait for approval. Then do the work, run both scripts, and stop. Show the test, the code and the suggested commit messages, and wait for "continue". Test code below is the target, so adapt names only if something fails to import.

### Cycle 1: a valid response returns the user (Zero)

**Red.** Create `tests/support/fixtures.ts` with a `validUser` sample user and `tests/support/fake-fetch.ts` with a `fakeFetch(body, status = 200)` helper that returns a function. The function records each URL in a `urls` array and resolves to `{ ok, status, json }`. Add `src/models/user.ts` with the `User` interface, and a stub `fetchUser` in `src/api/user-api.ts` that rejects with `new Error("not implemented")`. Then create `tests/api/user-api.test.ts`:

```ts
it("returns the user when the response is a valid user", async () => {
  const user = await fetchUser(1, fakeFetch(validUser));
  expect(user).toEqual(validUser);
});
```

Run it. It must fail on the stub's error, not on an import problem.

**Green.** Write the real path, with no hardcoded user. Add the `FetchFn` type. Call `fetchFn` with the URL built from `id`. Read `await response.json()` into a variable typed `unknown`. Add `isUser(value: unknown): value is User` to `src/guards/is-user.ts`, with the smallest check that makes the test pass: the value is a non-null object. If `isUser` fails, throw `new Error("Response is not a valid user")`. Otherwise return the body. There is no cast, because the guard narrows the type.

**Suggested commit messages.** `test: valid response returns the user`, then `feat: fetchUser reads the body as unknown and checks it with isUser`.

### Cycle 2: the request URL contains the id (One)

**Red.**

```ts
it("requests the JSONPlaceholder URL for the given id", async () => {
  const fetchFn = fakeFetch(validUser);
  await fetchUser(7, fetchFn);
  expect(fetchFn.urls).toEqual(["https://jsonplaceholder.typicode.com/users/7"]);
});
```

This test passes at once, because cycle 1 already had to build the URL to call `fetchFn`. Say so, and keep the test, because it pins the exact URL and the id that goes into it. Confirm it can fail by changing the URL in the code for a moment, then put it back.

**Green.** Nothing to add.

**Suggested commit message.** `test: request url contains the id`

### Cycle 3: a missing field is rejected (Boundary)

**Red.**

```ts
it("rejects when the response is missing the email field", async () => {
  const { email: _email, ...withoutEmail } = validUser;
  await expect(fetchUser(1, fakeFetch(withoutEmail))).rejects.toThrow(
    "Response is not a valid user",
  );
});
```

It fails because the guard only checks for an object, so the promise resolves.

**Green.** Make `isUser` check `"email" in value && typeof value.email === "string"`. Use `in` and `typeof` to narrow, one step at a time.

**Suggested commit messages.** `test: missing email is rejected`, then `feat: isUser checks email`.

### Cycle 4: every field and its type (Boundary)

**Red.** Use `it.each`, which runs one test over several inputs:

```ts
it.each([
  ["id is missing", { ...validUser, id: undefined }],
  ["id is a string", { ...validUser, id: "1" }],
  ["name is a number", { ...validUser, name: 42 }],
  ["address is missing", { ...validUser, address: undefined }],
  ["address has no city", { ...validUser, address: {} }],
  ["address.city is a number", { ...validUser, address: { city: 5 } }],
  ["body is null", null],
  ["body is a string", "not a user"],
  ["body is an array", [validUser]],
])("rejects when %s", async (_label, body) => {
  await expect(fetchUser(1, fakeFetch(body))).rejects.toThrow(
    "Response is not a valid user",
  );
});
```

Several cases fail because the guard checks only `email`. The `null`, string and array cases may already pass, which is fine.

**Green.** Complete `isUser`: check `id` is a number, `name` and `email` are strings, `address` is an object, and `address.city` is a string.

**Refactor.** Pull the repeated "is a non-null object" check into a small `isObject(value: unknown): value is object` helper, because `typeof null` is `"object"`. Use it for the body and for `address`. Tests stay green.

**Suggested commit messages.** `test: bad shapes are rejected`, `feat: isUser checks every field`, then `refactor: extract isObject`.

### Cycle 5: a failed request (Exceptional)

Two red-green steps, in this order.

**Red 1.**

```ts
it("rejects with the status when the request is not ok", async () => {
  await expect(fetchUser(9999, fakeFetch({}, 404))).rejects.toThrow(
    "Request failed with status 404",
  );
});
```

It fails because the `{}` body is rejected by `isUser` with a different message.

**Green 1.** When `response.ok` is false, throw an `Error` with the message `Request failed with status` and the status code, before the body is read.

**Red 2.**

```ts
it("rejects with context and the original error when the fetch itself fails", async () => {
  const networkError = new Error("network down");
  const offline = async () => {
    throw networkError;
  };
  await expect(fetchUser(1, offline)).rejects.toMatchObject({
    message: "Could not reach the API for user 1",
    cause: networkError,
  });
});
```

It fails because the rejection passes through unchanged, so the message is `network down`.

**Green 2.** Wrap only the `await fetchFn(...)` call in `try/catch`. In the `catch`, throw an `Error` with the message `Could not reach the API for user` and the id, passing the caught error as `{ cause: error }`. The status check and the body check stay outside the `try`.

**Suggested commit messages.** `test: http failure is rejected with the status`, `feat: throw on a bad status`, `test: a network error is rejected with context`, then `feat: wrap network errors with context and cause`.

### Cycle 6: final cleanup (Refactor)

This cycle adds no behaviour, so it has no new test. With every test green, make these changes one small step at a time, running both scripts after each:

1. Read every file in `src` top to bottom. Rename anything unclear.
2. Remove dead code and unused imports.
3. Give every exported function, type and interface a one-line doc comment.
4. Create `src/index.ts` that exports `User`, `isUser`, `fetchUser` and `FetchFn`. Do not change any test imports.
5. Run `npm run check` and `npm run build`. Confirm `dist/` holds only the `src` files and no tests.

**Suggested commit message.** `refactor: final cleanup and doc comments`

## Decisions

| Question | Decision |
| --- | --- |
| Why `unknown` for the response? | `response.json()` returns `any`, which switches the checker off. Assigning it to `unknown` forces a check before any field is used. |
| `any` and `as User`, or a type guard? | A type guard. A cast only tells the compiler to trust the data. The guard checks it, and the compiler then knows it is a `User`. |
| Why a type guard and not zod? | The task is to learn narrowing by hand. A schema library would hide it. |
| Why is the fetch function a parameter? | The test double is a plain function, so there is no mocking library and no network. The caller passes the real `fetch`. |
| How does `fetchUser` fail? | It throws, so the promise rejects. That is the normal way an async function fails. |
| Catch the network error? | Yes, around the fetch call only, and rethrow with context and the original error as `cause`. A bare `network down` does not say which request failed. The status and shape errors stay outside the `try`, so they are not wrapped twice. |
| Does the guard reject extra fields? | No. It checks only the fields in `User`. The real response has more, and a new field should not break the module. |
| Why `readonly` on `User`? | The data comes from outside and the module only reads it. |
| Why split `src` into `models`, `guards` and `api`? | Each folder has one job, so the type, the check and the network call can change independently. The tests mirror the same folders. |
| Why a separate `tsconfig.build.json`? | `tsconfig.json` includes `tests` so they are type-checked. The build should emit only `src`. |

## Final step: README, manual check and verification

Write `README.md` with these parts:

1. What it is and how to run it (`npm install`, `npm test`, `npm run typecheck`, `npm run check`, `npm run build`).
2. The design in a few lines.
3. The decisions above.
4. A short table mapping each cycle to its ZOMBIES letter.

The Key learnings, the reflection and the AI use section go in `part-1/day-06-typescript-in-practice.md`, in the user's own words.

**One manual check against the real API.** After `npm run build`, call the built `fetchUser` with the real `fetch` for id 1 and id 9999. Expect a typed user for 1 and a rejection with `Request failed with status 404` for 9999. Do not turn this into a test.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Writes async TypeScript with promises and async and await | `fetchUser` is an `async` function returning `Promise<User>` and uses `await` |
| Uses narrowing and type guards on external data | `isUser` narrows with `typeof` and `in`, and `fetchUser` narrows with it |
| Treats API responses as unknown until checked | The body variable is typed `unknown`, with no `any` and no `as` |
| Uses npm scripts for build and test | `test`, `typecheck`, `check` and `build` in `package.json` |
| Tests async code with Vitest and test doubles | `async` tests in `tests/api/user-api.test.ts` using `fakeFetch` from `tests/support/fake-fetch.ts` |
| Builds a typed API module test-first | `git log` reads test, feat, refactor in order for every cycle |
| Covers failure and missing-field cases | Cycles 3 to 5: missing `email`, bad shapes, 404, network error |

Finally, run `npm run check` and `npm run build` once more and suggest the commit message `docs: README and notes`. The user commits.
