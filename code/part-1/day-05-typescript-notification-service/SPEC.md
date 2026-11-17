# Notification Service in TypeScript: Build Spec for Claude Code


Rebuild one piece of the Day 2 notification service, `NotificationService.send`, in TypeScript with Vitest, strictly test-first. The Day 2 version is in `code/part-1/day-02-notification-service/src/notifications/service.py`. This is for the Day 5 assessment, so the order of tests and the commit history matter as much as the final code.

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every cycle, enter plan mode. The plan names the test you will write, the minimal code to pass it, and the refactor you expect. Write no files until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each red, green and refactor step, run `npm test` and `npm run typecheck`, give a suggested commit message, then wait.
3. **Red, green, refactor, never skipped.** Red: write one failing test and run it. Confirm it fails for the expected reason (an assertion, not a typo or an import error). Green: write the least code that makes it pass. Refactor: clean up while all tests stay green. If you find nothing to refactor, say why.
4. **One cycle at a time.** Never write production code before a failing test asks for it. Never write the next test before the current one is green.
5. **Stop after each cycle.** Show the test, the code and the suggested commit messages, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
6. **Simplest thing first.** Hardcoded returns are allowed early, because the next test will force the real logic. Do not add features no test asks for.
7. **Do not edit an old test to make a new one pass.** The only allowed edit to old tests is a pure refactor of shared setup, such as moving `FakeChannel` into its own file.
8. **No real sending.** No network, no email or SMS libraries. Dev dependencies only: `typescript` and `vitest`.
9. **Tests are ordered by ZOMBIES:** Zero, One, Many, then Boundary, Interface and Exceptional cases, always keeping scenarios and solutions simple.
10. **Keep notes.** Whenever a test changes the design, append one line to `NOTES.md`. The user will use these for the reflection.
11. **Reflection and AI use are the user's.** Do not write them in the day file.

TypeScript with `strict: true`. No `any`.

## Scope

**In**
- `NotificationService.send`
- A `Channel` interface, with a `FakeChannel` in the tests only
- A generic `Result<T>` with `ok` and `fail` helpers

**Out**
- Real channels (email, SMS, push) and their validation rules
- `send_many`
- Retries, async, logging, an error class hierarchy

## Python to TypeScript

| Day 2 (Python) | Day 5 (TypeScript) |
| --- | --- |
| `Channel` as a `Protocol` | `Channel` as an `interface` |
| Frozen `Notification` dataclass | `Notification` interface with `readonly` fields |
| `SendResult(channel, ok, error)` dataclass | Generic `Result<T>`, a discriminated union |
| `UnknownChannelError` raised | A failed `Result` returned |
| `dict[str, Channel]` | `Map<string, Channel>` |
| pytest fixtures | A `makeService` helper function |
| `pytest.mark.parametrize` | `it.each` |
| `pytest` | `vitest`, plus `tsc --noEmit` for the types |

## Design

The service knows nothing about email or SMS. It looks up a channel by name and hands it the notification. Every channel has the same `send` method.

| Piece | Job |
| --- | --- |
| `Notification` | Interface with readonly `to` and `body`. |
| `Channel` | Interface with `send(notification): void`. Throws if it cannot deliver. |
| `Result<T>` | `{ ok: true; value: T } \| { ok: false; error: string }`. |
| `ok`, `fail` | Generic helpers that build a `Result`. |
| `NotificationService` | Takes a `Map` of channel name to channel. Routes by name and returns a `Result`. |

```ts
interface Notification {
  readonly to: string;
  readonly body: string;
}

interface Channel {
  send(notification: Notification): void;
}

type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function ok<T>(value: T): Result<T>;
function fail<T = never>(error: string): Result<T>;
```

**Decisions made up front, so nothing is guessed**

- Constructor: `new NotificationService(channels: Map<string, Channel>)`. Channels are passed in, never created inside the service.
- `send(channelName: string, notification: Notification): Result<Notification>`. On success, `value` is the notification that was sent.
- An unknown channel name returns `fail(...)` and does not throw. The error message contains the name. Names are case-sensitive.
- A channel that throws does not throw out of the service. `send` returns `fail(message)`.
- In TypeScript a `catch` variable is `unknown`. If it is an `Error`, use its `message`. Otherwise use `String(thrown)`.
- No retries, no async, no logging.

## Folder layout

```
code/part-1/day-05-typescript-notification-service/
  package.json
  tsconfig.json
  .gitignore
  README.md
  NOTES.md
  SPEC.md
  src/
    models.ts      # Notification, Channel
    result.ts      # Result, ok, fail
    service.ts     # NotificationService
    index.ts       # public exports
  tests/
    fakes.ts       # FakeChannel
    service.test.ts
```

In the tests, use a `FakeChannel` from `fakes.ts` (records notifications, can be told to throw). That keeps the routing tests independent of any real channel.

## Step 0: Project setup

Do this before cycle 1. No tests or production code yet.

1. Create the folder and `npm init -y`. Install `typescript` and `vitest` as dev dependencies.
2. Add `tsconfig.json` with `strict: true`, target ES2022, `moduleResolution: bundler`, and `include` of `src` and `tests`.
3. Add scripts: `"test": "vitest run"` and `"typecheck": "tsc --noEmit"`.
4. Add a `.gitignore` with `node_modules/`. Create an empty `NOTES.md`.
5. Run `npm test` and confirm it reports "no test files found" (it exits with code 1, which is normal with no tests). `npm run typecheck` fails with `TS18003: No inputs were found` until a `.ts` file exists, and passes once cycle 1 adds files.

**Suggested commit message:** `chore: project skeleton with Vitest and strict tsconfig`

## The tests, in ZOMBIES order

| Tag | Test | Expectation |
| --- | --- | --- |
| Z1 | `a new service has sent nothing` | Channels stay empty after construction |
| O1 | `sending through %s reaches only that channel` | `it.each` over `"email"` and `"sms"`; that channel has the notification and the other has nothing |
| I1 | `a successful send returns ok with the notification as its value` | `result.ok` is true, `value` is the notification, and the types narrow on `ok` |
| B1 | `a failed result carries an error message and no value` | `fail("x")` is `{ ok: false, error: "x" }` |
| E1 | `an unknown channel name returns a failed result` | `it.each` over `"fax"`, `""`, `"EMAIL"`; the error contains the name; nothing is thrown |
| E2 | `a channel that throws gives a failed result with its message` | `{ ok: false, error: "gateway down" }` |
| E3 | `a channel that throws something that is not an Error still gives a failed result` | A thrown string becomes the error text |

## The cycles

Each cycle is red, green, refactor. Start every cycle in plan mode and wait for approval. Then do the work, run both scripts, and stop. Show the test, the code and the suggested commit messages, and wait for "continue". Test code below is the target, so adapt names only if something fails to import.

### Cycle 1: a new service has sent nothing (Zero)

**Red.** Create `tests/service.test.ts`. Define a small `FakeChannel` at the top of the file, then:

```ts
class FakeChannel implements Channel {
  sent: Notification[] = [];
  send(notification: Notification): void {
    this.sent.push(notification);
  }
}

it("a new service has sent nothing", () => {
  const email = new FakeChannel();
  const sms = new FakeChannel();
  new NotificationService(new Map([["email", email], ["sms", sms]]));
  expect(email.sent).toEqual([]);
  expect(sms.sent).toEqual([]);
});
```

Run it. It must fail because `NotificationService` does not exist.

**Green.** Create `models.ts` with `Notification` and `Channel`, and `service.ts` with a `NotificationService` whose constructor stores the map. Nothing else.

**Suggested commit messages.** `test: new service has sent nothing`, then `feat: NotificationService accepts channels`.

### Cycle 2: sending reaches only the named channel (One)

**Red.** Use `it.each`, which runs one test over several inputs, so email and sms are tested together:

```ts
it.each(["email", "sms"])("sending through %s reaches only that channel", (name) => {
  const channels = new Map([["email", new FakeChannel()], ["sms", new FakeChannel()]]);
  const service = new NotificationService(channels);
  const notification = { to: "someone", body: "hi" };
  service.send(name, notification);
  for (const [channelName, channel] of channels) {
    expect(channel.sent).toEqual(channelName === name ? [notification] : []);
  }
});
```

It fails because `send` does not exist (`service.send is not a function`).

**Green.** Add `send`, which looks the channel up by name with `this.channels.get(channelName)` and calls its `send`. Use a non-null assertion for now. Cycle 5 replaces it. Return type is `void` for now. There is no hardcoded email step, because the test covers both names at once.

**Refactor.** The setup will repeat in later tests. Move `FakeChannel` to `tests/fakes.ts` and add a `makeService()` helper that returns the service with its two fakes. Update the tests to use them. This is the one allowed edit to old tests, because behaviour does not change.

**Suggested commit messages.** `test: sending reaches only the named channel`, `feat: route by channel name`, then `refactor: extract FakeChannel and makeService`.

### Cycle 3: send returns a result (Interface)

**Red.**

```ts
it("a successful send returns ok with the notification as its value", () => {
  const { service } = makeService();
  const notification = { to: "a@x.com", body: "hi" };
  const result = service.send("email", notification);
  expect(result).toEqual({ ok: true, value: notification });
  if (result.ok) {
    expectTypeOf(result.value).toEqualTypeOf<Notification>();
  }
});
```

**Green.** Create `result.ts` with `Result<T>` and a generic `ok<T>(value: T)`. `send` returns `ok(notification)` after delivering, typed `Result<Notification>`.

**Suggested commit messages.** `test: a successful send returns ok with the notification`, then `feat: send returns Result with a generic ok helper`.

### Cycle 4: a failed result carries a message (Boundary)

**Red.**

```ts
it("a failed result carries an error message and no value", () => {
  const result: Result<Notification> = fail("gateway down");
  expect(result).toEqual({ ok: false, error: "gateway down" });
  if (!result.ok) {
    expectTypeOf(result.error).toEqualTypeOf<string>();
  }
});
```

It fails because `fail` does not exist.

**Green.** Add `fail<T = never>(error: string): Result<T>` to `result.ts`. Export `ok` and `fail`.

**Suggested commit messages.** `test: a failed result carries an error message`, then `feat: add the generic fail helper`.

### Cycle 5: unknown channel returns a failed result (Exceptional)

**Red.** Use `it.each`, which runs one test over several inputs:

```ts
it.each(["fax", "", "EMAIL"])("an unknown channel name %j returns a failed result", (name) => {
  const { service } = makeService();
  const result = service.send(name, { to: "a@x.com", body: "hi" });
  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.error).toContain(name);
  }
});
```

It fails because today a missing key crashes on `undefined.send`.

**Green.** In `send`, return `fail(...)` with the name in the message when the name is not in the map.

**Refactor.** Extract the lookup into a private `channelFor(channelName)` method that returns `Channel | undefined`, and have `send` call it. Tests stay green.

**Suggested commit messages.** `test: unknown channel names return a failed result`, `feat: reject unknown channels without throwing`, then `refactor: extract channelFor`.

### Cycle 6: a channel that throws gives a failed result (Exceptional)

**Red.** First extend `FakeChannel` in `tests/fakes.ts` with an optional `failWith` argument. When set, `send` throws `new Error(failWith)` instead of recording. Existing tests must stay green. Then:

```ts
it("a channel that throws gives a failed result with its message", () => {
  const service = new NotificationService(new Map([["email", new FakeChannel("gateway down")]]));
  const result = service.send("email", { to: "a@x.com", body: "hi" });
  expect(result).toEqual({ ok: false, error: "gateway down" });
});
```

**Green.** Wrap the channel call in `try/catch`. In the `catch`, return `fail(error.message)`. With `strict`, the variable is `unknown`, so narrow it with `error instanceof Error`.

**Refactor.** Move the `try/catch` and the result-building into a private `deliver(channel, notification)` method. `send` then reads: look up the channel, deliver. Tests stay green.

**Suggested commit messages.** `test: a channel that throws gives a failed result`, `feat: catch channel errors in send`, then `refactor: extract deliver`.

### Cycle 7: a thrown value that is not an Error (Exceptional)

**Red.**

```ts
it("a channel that throws something that is not an Error still gives a failed result", () => {
  const throwing: Channel = { send() { throw "plain string"; } };
  const service = new NotificationService(new Map([["email", throwing]]));
  const result = service.send("email", { to: "a@x.com", body: "hi" });
  expect(result).toEqual({ ok: false, error: "plain string" });
});
```

It fails because the `catch` only handles `Error` objects. This is the TypeScript difference worth noting: in Python, `except ChannelError` names the type. In TypeScript, anything can be thrown, so the `catch` has to check.

**Green.** In the `catch`, use `error instanceof Error ? error.message : String(error)`.

**Suggested commit messages.** `test: a thrown value that is not an Error gives a failed result`, then `feat: handle non-Error thrown values`.

### Cycle 8: final cleanup (Refactor)

This cycle adds no behaviour, so it has no new test. With every test green, make these changes one small step at a time, running both scripts after each:

1. Read `service.ts` and `result.ts` top to bottom. Rename anything unclear.
2. Remove dead code, unused imports and leftover non-null assertions.
3. Give every exported function, class and interface a one-line doc comment.
4. Create `src/index.ts` that exports `Notification`, `Channel`, `Result`, `ok`, `fail` and `NotificationService`. Do not change any test imports.

**Suggested commit message.** `refactor: final cleanup and public exports`

## Decisions

| Question | Decision |
| --- | --- |
| Unknown channel: throw or return? | Return `fail(...)`. Day 2 threw `UnknownChannelError`. Here the failure is part of the return type, so the caller has to handle it. |
| What is `T` in `Result<T>` for `send`? | The `Notification` that was sent. |
| Why a generic `Result<T>` and not the Day 2 `SendResult`? | To use generics in code written in this project. `SendResult` carried the channel name, which the caller already has. |
| Why both a generic and a union in `Result<T>`? | The generic (`T`) sets the type of the success value. The union ties `ok` to the other fields, so checking `ok` narrows to `value` or `error`, and the compiler rejects impossible states such as `{ ok: true, error: "x" }`. Day 2's `SendResult` had optional fields instead. |
| Does a failed result carry a value? | No. The union has no `value` on the failed side, so the compiler stops code that reads it. |
| Thrown value that is not an `Error`? | Use `String(thrown)` as the error text. |
| Case-sensitive names? | Yes. `"EMAIL"` is unknown. |
| `class` or `interface` for `Notification`? | `interface`. It is data only, so there is no runtime object. |

## Final step: README and checks

Write `README.md` with these parts:

1. What it is and how to run it (`npm install`, `npm test`, `npm run typecheck`).
2. The design in a few lines, and how it differs from Day 2 (link the Python files).
3. The decisions above.
4. A short table mapping each cycle to its ZOMBIES letter.

The Key learnings, the reflection and the AI use section go in `part-1/day-05-typescript-foundations.md`, in the user's own words.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Explains how TypeScript differs from Python | The "Python to TypeScript" table, cycle 7, and the day file's key learnings |
| Uses interfaces and union types and generics | `Notification` and `Channel` interfaces. `Result<T>` is a discriminated union. `ok<T>` and `fail<T>` are generic functions. |
| Sets up a TypeScript project with tests | `package.json`, `tsconfig.json` (strict), Vitest. `npm test` and `npm run typecheck` pass. |
| Rebuilds a small service in TypeScript test-first | `git log` reads test, feat, refactor in order for every cycle |
| Reflects on moving between the two languages | The day file's reflection, written by the user |

Finally, run `npm test` and `npm run typecheck` once more and suggest the commit message `docs: README and notes`. The user commits.
