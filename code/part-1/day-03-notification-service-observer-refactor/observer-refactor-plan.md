# Notification Service: Observer Refactor Plan for Claude Code

Oct 30, 2026 · @Ankit

## Instructions for Claude Code

Extend the existing notification service with the Observer pattern, strictly test-first, with every existing test staying green. This is for a training assessment, so the order of tests and the commit history matter as much as the final code. The original build plan (`notification-service-plan.md`) is already done and committed. Follow the cycles in this doc in order.

**Ground rules**

1. **Always use plan mode.** Before every cycle, enter plan mode. The plan names the test you will write, the minimal code to pass it, and the refactor you expect. Write no files until the user approves the plan.
2. **Never commit, and never change git state.** Do not run `git add`, `git commit`, `git switch`, `git checkout` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user creates the branch and makes every commit. After each red, green and refactor step, run the full test suite and give a suggested commit message, then wait.
3. **Red, green, refactor, never skipped.** Red: write one failing test and run it. Confirm it fails for the expected reason. Green: write the least code that makes it pass. Refactor: clean up while all tests stay green. If you find nothing to refactor, say why.
4. **One cycle at a time.** Never write production code before a failing test asks for it. Never write the next test before the current one is green.
5. **Stop after each cycle.** Show the test, the code and the suggested commit messages, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
6. **Simplest thing first.** Do not add features no test asks for.
7. **Do not edit any existing test.** Old tests are the safety net. New tests go in a new file, `tests/test_observers.py`. Adding a new class to `tests/fakes.py` is allowed, because it does not change any old test. Changing an existing class there is not allowed.
8. **Some new tests may pass immediately.** When that happens, say so, explain why it passed, and treat it as a safety-net test, not a design-driving one.
9. **No new dependencies.** Only `pytest`. No async, no queues, no logging framework. Observers run in the same process, synchronously.
10. **Tests are ordered by ZOMBIES:** Zero, One, Many, then Boundary, Interface and Exceptional cases, always keeping scenarios and solutions simple.
11. **Keep notes.** Whenever a test changes the design, append one line to `NOTES.md`. The user will use these for the reflection question.

Python 3.11 or newer, with type hints.

## Design

Routing does not change. `send("email", n)` still looks up one channel by name and returns one `SendResult`. That part stays as it is, and it is why every old test stays green.

What is new is that the service becomes the **subject**. After each delivery attempt it tells every subscribed **observer** what happened. The service does not know what observers do with the event (audit log, metrics, alerts).

| Piece | Job |
| --- | --- |
| `Observer` | A `Protocol` with `on_delivery(notification, result) -> None`. |
| `NotificationService.subscribe(observer)` | Adds an observer. Observers are notified in the order they subscribed. |
| `NotificationService.unsubscribe(observer)` | Removes an observer. |
| `NotificationService._notify(notification, result)` | Private. Calls every observer. Called from `_deliver`, so `send` and `send_many` are both covered. |

**Decisions made up front, so nothing is guessed**

- The constructor stays `NotificationService(channels: dict[str, Channel])`. The observer list starts empty.
- Observers are notified after every delivery attempt, successful or failed, with the same `SendResult` that is returned to the caller.
- An unknown channel name raises `UnknownChannelError` before any delivery, so no observer is notified.
- An observer that raises must never break delivery or stop other observers from being notified. The exception is swallowed in `_notify`. This matches the existing rule that one failing channel does not stop the others.
- Unsubscribing an observer that is not subscribed raises `ValueError` (the behavior of `list.remove`). This is pinned by a test in cycle O6.
- Subscribing the same observer twice is out of scope. Do not handle it.
- No retries, no async, no event history.

**Files touched**

```
src/notifications/
  observers.py      # NEW: Observer protocol
  service.py        # subscribe, unsubscribe, _notify, call from _deliver
  __init__.py       # export Observer
tests/
  fakes.py          # ADD FakeObserver (new class only)
  test_observers.py # NEW
NOTES.md            # append design notes
README.md           # add an Observer section at the end
```

`channels.py`, `models.py`, `test_service.py`, `test_channels.py` and `test_push_channel.py` must not change.

## Step 0: Setup

Do this before cycle O1. No new tests or production code yet.

1. **The user** creates a branch: `git switch -c feature/observer`. Claude Code does not run this.
2. Run the full suite and confirm it is green. Report the number of passing tests. This is the baseline.
3. Add `FakeObserver` to `tests/fakes.py` and create an empty `tests/test_observers.py`:

```python
class FakeObserver:
    def __init__(self):
        self.events = []

    def on_delivery(self, notification, result):
        self.events.append((notification, result))
```

4. Run the full suite again. It must show the same count as the baseline.

**Suggested commit message:** `chore: add FakeObserver test double`

## The cycles

Each cycle is red, green, refactor. Start every cycle in plan mode and wait for approval. Then do the work, run the full suite, and stop. Show the user the test, the code and the suggested commit messages, and wait for "continue". Test code below is the target, so adapt names only if something fails to import.

### Cycle O1: an observer is told about a successful delivery (One)

**Red.** In `tests/test_observers.py`:

```python
from notifications.models import Notification, SendResult
from fakes import FakeObserver


def test_observer_receives_successful_delivery(service):
    observer = FakeObserver()
    service.subscribe(observer)
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    service.send("email", n)
    assert observer.events == [(n, SendResult(channel="email", ok=True))]
```

Run it. It must fail with an `AttributeError` because `subscribe` does not exist.

**Green.** Create `observers.py` with the `Observer` protocol. In `service.py`, add `self._observers: list[Observer] = []` to `__init__`, a `subscribe` method, and a private `_notify` that loops over the observers. Call `_notify` inside `_deliver`, after the result is built and before it is returned.

**Suggested commit messages.** `test: observer receives successful delivery`, then `feat: add subscribe and notify observers`.

### Cycle O2: an observer is told about a failed delivery (One)

**Red.**

```python
from notifications.service import NotificationService
from fakes import FakeChannel


def test_observer_receives_failed_delivery():
    service = NotificationService({"email": FakeChannel(fail_with="down")})
    observer = FakeObserver()
    service.subscribe(observer)
    n = Notification(to="a@x.com", body="hi")
    service.send("email", n)
    assert observer.events == [(n, SendResult(channel="email", ok=False, error="down"))]
```

This should pass with no production change, because `_notify` already runs for both outcomes. Say so and explain why. It is a safety-net test.

**Suggested commit message.** `test: observer receives failed delivery`

### Cycle O3: many observers, and send_many (Many)

**Red.**

```python
def test_all_observers_notified_once_per_channel(service):
    first, second = FakeObserver(), FakeObserver()
    service.subscribe(first)
    service.subscribe(second)
    service.send_many(["email", "sms"], Notification(to="a@x.com", body="hi"))
    assert [r.channel for _, r in first.events] == ["email", "sms"]
    assert first.events == second.events
```

This should also pass with no production change, because `send_many` goes through `_deliver`. Say so and explain why.

**Suggested commit message.** `test: observers notified once per channel`

### Cycle O4: an unknown channel notifies nobody (Boundary)

**Red.**

```python
import pytest
from notifications.models import UnknownChannelError


def test_unknown_channel_notifies_nobody(service):
    observer = FakeObserver()
    service.subscribe(observer)
    with pytest.raises(UnknownChannelError):
        service.send_many(["email", "fax"], Notification(to="a@x.com", body="hi"))
    assert observer.events == []
```

This should pass because `send_many` already validates all names before delivering (cycle 8 of the original plan). Say so. It pins the decision that no delivery means no event.

**Suggested commit message.** `test: unknown channel notifies no observers`

### Cycle O5: unsubscribe (Boundary)

**Red.**

```python
def test_unsubscribed_observer_is_not_notified(service):
    observer = FakeObserver()
    service.subscribe(observer)
    service.unsubscribe(observer)
    service.send("email", Notification(to="a@x.com", body="hi"))
    assert observer.events == []
```

It fails because `unsubscribe` does not exist.

**Green.** Add `unsubscribe`, which removes the observer from the list.

**Suggested commit messages.** `test: unsubscribed observer is not notified`, then `feat: add unsubscribe`.

### Cycle O6: unsubscribing a stranger raises (Boundary)

**Red.**

```python
def test_unsubscribing_unknown_observer_raises(service):
    with pytest.raises(ValueError):
        service.unsubscribe(FakeObserver())
```

This should pass with no production change, because `list.remove` already raises `ValueError`. Say so. The test exists to pin the decision, so a later change cannot silently alter it.

**Suggested commit message.** `test: unsubscribing unknown observer raises`

### Cycle O7: a broken observer does not break delivery (Exceptional)

**Red.** Define the exploding observer at the top of `tests/test_observers.py`, then:

```python
class ExplodingObserver:
    def on_delivery(self, notification, result):
        raise RuntimeError("boom")


def test_failing_observer_does_not_break_delivery(service, email_channel):
    good = FakeObserver()
    service.subscribe(ExplodingObserver())
    service.subscribe(good)
    n = Notification(to="a@x.com", body="hi")
    assert service.send("email", n).ok
    assert email_channel.sent == [n]
    assert len(good.events) == 1
```

It fails because the `RuntimeError` escapes `_notify`.

**Green.** In `_notify`, wrap each observer call in `try/except Exception` so one bad observer cannot stop the rest. Append a line to `NOTES.md`, for example: "Observer errors are isolated, to match how channel failures are handled."

**Refactor.** Read `_deliver` and `_notify`. `_deliver` should read: attempt the send, build the result, notify, return. Add type hints and a one-line docstring to `subscribe`, `unsubscribe` and `_notify`. Export `Observer` from `__init__.py` without changing any test imports. Run all tests green.

**Suggested commit messages.** `test: failing observer does not break delivery`, `feat: isolate observer errors`, then `refactor: tidy _deliver and document observer API`.

## Final step: README and checks

Add an **Observer** section at the end of `README.md`:

1. What it is: the service announces each delivery result to subscribed observers.
2. How to add an observer in three steps: write a class with `on_delivery(notification, result)`, call `service.subscribe(it)`, call `service.unsubscribe(it)` when done.
3. The decisions listed under Design.
4. A short note that routing is unchanged: Strategy decides how a message is delivered, Observer announces what happened afterwards.
5. A table mapping each cycle to its ZOMBIES letter.
6. **Reflection:** where did writing the test first change the design? Claude Code may draft this from `NOTES.md`, but the user must rewrite it in their own words and only keep what they genuinely noticed.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Observer applied to a real refactor | `subscribe`, `unsubscribe` and `_notify` in `service.py` |
| Tests stay green | The full suite passes after every step, with the baseline count plus the new tests |
| No existing test changed | `git diff --stat` against the branch start lists no old test file |
| New behavior built test-first | A failing test before production code in cycles O1, O5 and O7. O2, O3, O4 and O6 are safety nets and are labeled as such. |
| Refactoring is visible | A `refactor:` commit at the end of cycle O7 |
| Design is open to extension | A new observer needs no change to `service.py` |

Run `git status` and `git diff --stat` (read-only) and paste the output into the README. The files listed must match the "Files touched" section above and nothing else.

Finally, run the whole suite once more and suggest the commit message `docs: README and notes for observer`. The user commits.
