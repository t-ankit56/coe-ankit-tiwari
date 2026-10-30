# Day 2 — Notification service (test-first)

A small notification service that sends email, SMS and push notifications through one interface, built test-first with pytest. Nothing is really sent: each channel records messages in memory.

## Setup

```bash
cd code/part-1/day-02-notification-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test

```bash
pytest -v
```

27 tests in `tests/`: `test_service.py` (routing, with a `FakeChannel`), `test_channels.py` (email and SMS) and `test_push_channel.py` (the channel added last).

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
