# Day 5 — Notification service in TypeScript (test-first)

`NotificationService.send` from the [Day 2 Python service](../day-02-notification-service/), rebuilt in TypeScript with Vitest. It routes a notification to a channel by name and returns a `Result`. Nothing is really sent: the tests use a `FakeChannel`.

Only `send` is rebuilt. Real channels, `send_many`, retries and async are out of scope. The full build spec is in [SPEC.md](SPEC.md).

## Setup

```bash
cd code/part-1/day-05-typescript-notification-service
npm install
```

## Test

```bash
npm test            # Vitest: 10 tests in tests/service.test.ts
npm run typecheck   # tsc --noEmit, strict mode
```

Run both. The `expectTypeOf` checks in the tests only do something under `typecheck`.

## Design

- `NotificationService` (`src/service.ts`) takes a `Map` of channel name to channel and routes by name. It knows nothing about email or SMS.
- A channel is anything with `send(notification)` that throws if it cannot deliver (the `Channel` interface in `src/models.ts`).
- `Notification` is an interface with `readonly` fields (`src/models.ts`).
- `Result<T>` (`src/result.ts`) is a generic discriminated union: `{ ok: true; value: T } | { ok: false; error: string }`. `ok` and `fail` are generic helpers that build it. Checking `result.ok` tells the compiler whether `value` or `error` exists.

```ts
import { NotificationService, type Channel } from "./src";

const email: Channel = { send(n) { console.log("email to", n.to); } };
const service = new NotificationService(new Map([["email", email]]));

const result = service.send("email", { to: "a@x.com", body: "hi" });
if (result.ok) {
  result.value;   // the Notification that was sent
} else {
  result.error;   // string
}
service.send("fax", { to: "a@x.com", body: "hi" });
// { ok: false, error: 'unknown channel "fax"' }
```

### Differences from Day 2

| Day 2 (Python) | Day 5 (TypeScript) |
| --- | --- |
| [`Channel` as a `Protocol`](../day-02-notification-service/src/notifications/channels.py) | `Channel` as an `interface` |
| Frozen `Notification` dataclass | `Notification` interface with `readonly` fields |
| `SendResult(channel, ok, error)` dataclass | Generic `Result<T>`, a discriminated union |
| [`UnknownChannelError` raised](../day-02-notification-service/src/notifications/service.py) | A failed `Result` returned |
| `dict[str, Channel]` | `Map<string, Channel>` |
| `pytest.mark.parametrize` | `it.each` |

## Decisions

- `send(channelName, notification)` returns `Result<Notification>`. On success, `value` is the notification that was sent.
- An unknown channel name returns `fail(...)` and does not throw. The message contains the name. Names are case-sensitive.
- A channel that throws does not throw out of the service. `send` returns `fail(message)`.
- A `catch` variable is `unknown` in TypeScript. An `Error` gives its `message`. Anything else is turned into text with `String(thrown)`.
- `Notification` is an `interface`, not a class, because it is only data.
- No retries, no async, no logging.

More reasoning is in the Decisions table of [SPEC.md](SPEC.md#decisions), and the design changes the tests forced are in [NOTES.md](NOTES.md).

## How ZOMBIES guided the test order

| Cycle | Letter | Test |
| --- | --- | --- |
| 1 | Zero | a new service has sent nothing |
| 2 | One | sending through a channel name reaches only that channel (`it.each` over email and sms) |
| 3 | Interface | a successful send returns ok with the notification as its value |
| 4 | Boundary | a failed result carries an error message and no value |
| 5 | Exceptional | an unknown channel name returns a failed result |
| 6 | Exceptional | a channel that throws gives a failed result with its message |
| 7 | Exceptional | a channel that throws something that is not an Error still gives a failed result |
| 8 | Refactor | final cleanup and public exports (no new test) |

The commit history shows `test:`, `feat:` and `refactor:` commits in that order for each cycle.
