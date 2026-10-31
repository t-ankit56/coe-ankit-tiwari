# Day 3 — Notification service with Observer

The [Day 2 notification service](../day-02-notification-service/), extended test-first with the Observer pattern: the service now tells subscribed observers about every delivery. The sections up to the Day 2 test order describe the code this builds on; [Observer](#observer) at the end covers what Day 3 added.

A small notification service that sends email, SMS and push notifications through one interface, built test-first with pytest. Nothing is really sent: each channel records messages in memory.

## Setup

```bash
cd code/part-1/day-03-notification-service-observer-refactor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test

```bash
pytest -v
```

34 tests in `tests/`: `test_service.py` (routing, with a `FakeChannel`), `test_channels.py` (email and SMS), `test_push_channel.py` (the channel added last on Day 2) and `test_observers.py` (observers, with a `FakeObserver`).

## Design

- `NotificationService` (`service.py`) takes a dict of channel name to channel and routes by name. It knows nothing about email or SMS.
- A channel is anything with `send(notification)` that raises `ChannelError` when it can't deliver (the `Channel` protocol in `channels.py`).
- `EmailChannel`, `SmsChannel` and `PushChannel` share a small `_RecordingChannel` base: validate, then record in `sent`. Each one adds only its own recipient rule.
- `Notification` and `SendResult` are frozen dataclasses (`models.py`).

```python
from notifications import EmailChannel, Notification, NotificationService, SmsChannel

service = NotificationService({"email": EmailChannel(), "sms": SmsChannel()})
service.send_many(["email", "sms"], Notification(to="a@x.com", body="hi"))
# [SendResult(channel='email', ok=True, error=None),
#  SendResult(channel='sms', ok=False, error='sms number must be 7 to 15 digits, optional leading +')]
```

### Adding a channel

1. Write a class with `send(notification)`, or subclass `_RecordingChannel` and supply `_validate`.
2. Raise `ChannelError` when it can't deliver.
3. Pass it into the service dict under a new name.

`PushChannel` was added this way with no change to `service.py` or any existing test. The proof is in [Exercise 3 of the day file](../../../part-1/day-02-tdd-in-python.md#exercise-3-add-a-new-channel-without-changing-existing-tests).

## Decisions

- `send(name, notification)` returns a `SendResult`; `send_many(names, notification)` returns one per channel, in the order given.
- An unknown channel name raises `UnknownChannelError`. Names are case-sensitive.
- `send_many` checks every name before sending anything, so a bad name means nothing is sent.
- A `ChannelError` from a channel becomes `SendResult(ok=False, error=...)` and never stops the other channels.
- Email needs `@` in `to`. SMS needs 7 to 15 digits with an optional leading `+`. Push needs a non-empty device token. All channels reject an empty body.
- No real sending, retries, async or logging. The only dependency is pytest.

## Test order (ZOMBIES)

| Cycle | What the test drove | ZOMBIES |
| --- | --- | --- |
| 1 | New service has sent nothing | Zero |
| 2 | Send via email reaches only email | One |
| 3 | Send via SMS forces routing by name | One |
| 4 | `send` returns a `SendResult` | Interface |
| 5 | Unknown names raise (parametrized) | Exceptional |
| 6 | `send_many` reaches every channel in order | Many |
| 7 | A failing channel gives `ok=False`; the others still run | Exceptional |
| 8 | An unknown name in `send_many` sends nothing | Boundary |
| 9 | `EmailChannel`: empty, records, bad recipient, empty body | Zero, One, Exceptional |
| 10 | `SmsChannel`: empty, records, bad number, empty body | Zero, One, Exceptional |
| 11 | End to end with the real channels | Simple scenario |
| 12 | Cleanup: type hints, `Channel` protocol, exports (no new test) | — |
| 13 | `PushChannel`: empty, delivers through the service, empty token | Zero, One, Exceptional |

## Observer

The service is now the subject. After every delivery attempt it tells each subscribed observer the notification and the same `SendResult` it returns to the caller. It doesn't know what an observer does with that, such as an audit log, metrics or alerts.

### Adding an observer

1. Write a class with `on_delivery(notification, result)` (the `Observer` protocol in `observers.py`).
2. Call `service.subscribe(it)`.
3. Call `service.unsubscribe(it)` when it should stop listening.

```python
from notifications import EmailChannel, Notification, NotificationService


class FailureCounter:
    def __init__(self):
        self.failures = 0

    def on_delivery(self, notification, result):
        if not result.ok:
            self.failures += 1


service = NotificationService({"email": EmailChannel()})
counter = FailureCounter()
service.subscribe(counter)
service.send("email", Notification(to="no-at-sign", body="hi"))
counter.failures  # 1
```

No change to `service.py` is needed for a new observer.

### Observer decisions

- Observers are told after every delivery attempt, success or failure, with the same `SendResult` the caller gets.
- `send` and `send_many` both go through `_deliver`, so one `_notify` call covers both.
- An unknown channel name raises `UnknownChannelError` before any delivery, so no observer is told anything.
- An observer that raises is ignored (`contextlib.suppress` in `_notify`). It never breaks delivery or stops the other observers. This matches how a failing channel never stops the other channels.
- Observers are told in the order they subscribed.
- Unsubscribing an observer that was never subscribed raises `ValueError` (from `list.remove`).
- Subscribing the same observer twice is out of scope. No retries, no async, no event history.

### Strategy and Observer

Routing is unchanged. The channels are the Strategy: they decide how a message is delivered, and the service picks one by name. The observers are the Observer: they hear what happened afterwards.

### Cycle order (ZOMBIES)

| Cycle | What the test pinned | ZOMBIES | Kind |
| --- | --- | --- | --- |
| Step 0 | `FakeObserver` test double, empty `test_observers.py` | — | Setup |
| O1 | An observer receives a successful delivery | One | Red, then green (`subscribe`, `_notify`) |
| O2 | An observer receives a failed delivery | One | Safety net (passed at once) |
| O3 | Every observer is told once per channel in `send_many` | Many | Safety net |
| O4 | An unknown channel notifies nobody | Boundary | Safety net |
| O5 | An unsubscribed observer is not told | Boundary | Red, then green (`unsubscribe`) |
| O6 | Unsubscribing an unknown observer raises | Boundary | Safety net |
| O7 | A failing observer doesn't break delivery | Exceptional | Red, green, then refactor |

The safety-net tests passed without production changes, because earlier code already behaved that way. They lock in the decisions, so they have a `test:` commit and no `feat:` commit.

### No existing test changed

Files changed between the baseline copy (`40ff3fd`) and the last code commit (`ad8c943`):

```
$ git diff --stat 40ff3fd ad8c943 -- code/part-1/day-03-notification-service-observer-refactor
 .../NOTES.md                                       |  6 ++
 .../src/notifications/__init__.py                  |  2 +
 .../src/notifications/observers.py                 |  9 +++
 .../src/notifications/service.py                   | 27 ++++++++-
 .../tests/fakes.py                                 |  8 +++
 .../tests/test_observers.py                        | 66 ++++++++++++++++++++++
 6 files changed, 115 insertions(+), 3 deletions(-)
```

`tests/fakes.py` only gained the new `FakeObserver` class. `test_service.py`, `test_channels.py`, `test_push_channel.py`, `channels.py` and `models.py` aren't in the list. This README is changed in the docs commit after these.

### Reflection

*Where did writing the test first change the design?* (Notes per cycle are in [NOTES.md](NOTES.md).)
