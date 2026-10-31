# Notification Service: TDD Build Plan for Claude Code

Oct 29, 2026 · @Ankit

## Instructions for Claude Code

Build a small notification service in Python with pytest, strictly test-first. This is for a TDD assessment, so the commit history and the order of tests matter as much as the final code. Follow the cycles in this doc in order.

**Ground rules**

1. **Always use plan mode.** Before every cycle, enter plan mode. The plan names the test you will write, the minimal code to pass it, and the refactor you expect. Write no files until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as \`git status\` and \`git diff\` are fine. The user makes every commit. After each red, green and refactor step, run the full test suite and give a suggested commit message, then wait.
3. **Red, green, refactor, never skipped.** Red: write one failing test and run it. Confirm it fails for the expected reason. Green: write the least code that makes it pass. Refactor: clean up while all tests stay green. The refactor steps named in each cycle are expected. If you find nothing to refactor, say why.
4. **One cycle at a time.** Never write production code before a failing test asks for it. Never write the next test before the current one is green.
5. **Stop after each cycle.** Show the test, the code and the suggested commit messages, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
6. **Simplest thing first.** Hardcoded returns are allowed early, because the next test will force the real logic. Do not add features no test asks for.
7. **Do not edit an old test to make a new one pass.** The only allowed edit to old tests is a pure refactor of shared setup, such as moving it into a fixture.
8. **No real sending.** No network, no email or SMS libraries. Channels record messages in memory. Only dependency: `pytest`.
9. **Tests are ordered by ZOMBIES:** Zero, One, Many, then Boundary, Interface and Exceptional cases, always keeping scenarios and solutions simple.
10. **Keep notes.** Whenever a test changes the design (for example, forcing a constructor parameter), append one line to `NOTES.md`. The user will use these for the reflection question in the brief.

Python 3.11 or newer, with type hints.

## Design

The service knows nothing about email or SMS. It looks up a channel by name and hands it the message. Every channel has the same `send` method, so a new channel never requires changing the service.

| Piece | Job |
| --- | --- |
| `Notification` | Frozen dataclass with `to`, `body` and an optional `subject` (used by email only). |
| `Channel` | A `Protocol` (any class with a matching `send` method counts) with `send(notification) -> None`. Raises `ChannelError` if it cannot deliver. |
| `EmailChannel`, `SmsChannel` | Validate the input, then record the message in an in-memory `sent` list. Nothing is really sent. |
| `NotificationService` | Takes a dict of channel name to channel. Routes by name and returns results. |
| `SendResult` | Frozen dataclass with `channel`, `ok` and `error`. |

**Decisions made up front, so nothing is guessed**

- Constructor: `NotificationService(channels: dict[str, Channel])`. Channels are passed in, never created inside the service.
- `send(channel_name, notification) -> SendResult`.
- `send_many(channel_names, notification) -> list[SendResult]`, one result per channel, in the order given.
- Unknown channel name raises `UnknownChannelError`. Names are case-sensitive.
- A channel failing does not raise out of the service. The service catches `ChannelError` and returns `SendResult(ok=False, error=...)`. In `send_many`, a failure never stops the other channels.
- Both channels reject an empty body. Email requires `@` in `to`. SMS requires 7 to 15 digits, with an optional leading `+`.
- No retries, no async, no logging framework. Keep it small.

**Folder layout**

```
(repo root)/
  pyproject.toml
  README.md
  NOTES.md
  src/notifications/
    __init__.py
    models.py       # Notification, SendResult, errors
    channels.py     # Channel protocol, EmailChannel, SmsChannel
    service.py      # NotificationService
  tests/
    conftest.py     # shared fixtures
    fakes.py        # FakeChannel
    test_service.py
    test_channels.py
```

In service tests, use a `FakeChannel` from `fakes.py` (records messages, can be told to fail). That keeps routing tests independent of the real channels.

## Step 0: Project setup

Do this before cycle 1. No tests or production code yet.

1. Create the folder structure above inside the existing repo, with empty files and an empty `tests/`.
2. Add `pyproject.toml` with the project name, Python 3.11 or newer, `pytest` as a dev dependency, and this pytest config so tests can import from `src`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

3. Create a virtual environment and install pytest. Run `pytest` and confirm it reports "no tests ran" without errors.
4. Git is already set up. Do not run `git init`. Append `.venv/`, `__pycache__/` and `.pytest_cache/` to the existing `.gitignore`, adding only the lines that are missing and never overwriting the file. Create an empty `NOTES.md`.

**Suggested commit message:** `chore: project skeleton with pytest config`

## The cycles

Each cycle is red, green, refactor. Start every cycle in plan mode and wait for approval. Then do the work, run the full suite, and stop. Show the user the test, the code and the suggested commit messages, and wait for "continue". Test code below is the target, so adapt names only if something fails to import.

### Cycle 1: a new service has sent nothing (Zero)

**Red.** Create `tests/test_service.py`. Define a small `FakeChannel` at the top of the file (it records messages in a `sent` list), then:

```python
class FakeChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)


def test_new_service_has_sent_nothing():
    email, sms = FakeChannel(), FakeChannel()
    NotificationService({"email": email, "sms": sms})
    assert email.sent == [] and sms.sent == []
```

Run it. It must fail with an import error because `NotificationService` does not exist.

**Green.** Create `service.py` with a `NotificationService` whose `__init__(self, channels)` stores the dict. Nothing else.

**Suggested commit messages.** `test: new service has sent nothing`, then `feat: NotificationService accepts channels`.

### Cycle 2: send by email reaches only the email channel (One)

**Red.**

```python
def test_send_via_email_reaches_only_email_channel():
    email, sms = FakeChannel(), FakeChannel()
    service = NotificationService({"email": email, "sms": sms})
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    service.send("email", n)
    assert email.sent == [n]
    assert sms.sent == []
```

**Green.** Add the frozen `Notification` dataclass to `models.py` (`to`, `body`, `subject=None`). Add `send` that hardcodes the email channel: `self._channels["email"].send(notification)`. Yes, hardcoded on purpose. The next test will expose it.

**Suggested commit messages.** `test: send via email reaches only email channel`, then `feat: send routes to the email channel`.

### Cycle 3: send by SMS reaches only the SMS channel (One)

**Red.**

```python
def test_send_via_sms_reaches_only_sms_channel():
    email, sms = FakeChannel(), FakeChannel()
    service = NotificationService({"email": email, "sms": sms})
    n = Notification(to="+919876543210", body="hi")
    service.send("sms", n)
    assert sms.sent == [n]
    assert email.sent == []
```

It fails because the code always picks email.

**Green.** Route by name: `self._channels[channel_name].send(notification)`.

**Refactor.** Both tests repeat their setup. Move `FakeChannel` to `tests/fakes.py`. In `tests/conftest.py` add pytest fixtures `email_channel`, `sms_channel` and `service` (a `NotificationService` built from those two). Rewrite the two tests to use the fixtures. This is the one allowed edit to old tests, because behavior does not change. Run all tests green.

**Suggested commit messages.** `test: send via sms reaches only sms channel`, `feat: route by channel name`, then `refactor: extract FakeChannel and fixtures`.

### Cycle 4: send returns a result (Boundary and Interface)

**Red.**

```python
def test_send_returns_successful_result(service):
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    assert service.send("email", n) == SendResult(channel="email", ok=True, error=None)
```

**Green.** Add the frozen `SendResult` dataclass to `models.py` (`channel`, `ok`, `error=None`). `send` returns `SendResult(channel_name, True)` after delivering.

**Suggested commit messages.** `test: send returns a successful result`, then `feat: send returns SendResult`.

### Cycle 5: unknown channel is rejected (Exceptional)

**Red.** Use `parametrize`, which runs one test over several inputs:

```python
@pytest.mark.parametrize("name", ["fax", "", "EMAIL"])
def test_unknown_channel_raises(service, name):
    with pytest.raises(UnknownChannelError):
        service.send(name, Notification(to="a@x.com", body="hi"))
```

It fails because today a missing key raises `KeyError`.

**Green.** Add `UnknownChannelError(ValueError)` to `models.py`. In `send`, raise it when the name is not in the dict.

**Refactor.** Extract the lookup and the error into a private `_channel_for(channel_name)` method, and have `send` call it. Tests stay green.

**Suggested commit messages.** `test: unknown channel names raise`, `feat: reject unknown channels`, then `refactor: extract _channel_for`.

### Cycle 6: send to many channels at once (Many)

**Red.**

```python
def test_send_many_delivers_once_per_channel_in_order(service, email_channel, sms_channel):
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    results = service.send_many(["email", "sms"], n)
    assert [r.channel for r in results] == ["email", "sms"]
    assert all(r.ok for r in results)
    assert email_channel.sent == [n]
    assert sms_channel.sent == [n]
```

**Green.** Add `send_many` as a loop that calls `send` for each name and collects the results.

**Suggested commit messages.** `test: send_many reaches every channel in order`, then `feat: add send_many`.

### Cycle 7: a failing channel does not break the others (Exceptional)

**Red.** First extend `FakeChannel` in `tests/fakes.py` with an optional `fail_with` argument. When set, `send` raises `ChannelError(fail_with)` instead of recording. Existing tests must stay untouched and green. Then:

```python
def test_failed_channel_gives_failed_result():
    service = NotificationService({"email": FakeChannel(fail_with="gateway down")})
    result = service.send("email", Notification(to="a@x.com", body="hi"))
    assert result == SendResult(channel="email", ok=False, error="gateway down")


def test_send_many_continues_after_a_failure():
    sms = FakeChannel()
    service = NotificationService({"email": FakeChannel(fail_with="down"), "sms": sms})
    results = service.send_many(["email", "sms"], Notification(to="+919876543210", body="hi"))
    assert [r.ok for r in results] == [False, True]
    assert len(sms.sent) == 1
```

Write these one at a time, each with its own red and green.

**Green.** Add `ChannelError` to `models.py`. In `send`, wrap the channel call in `try/except ChannelError` and return `SendResult(channel_name, False, str(error))`. `send_many` already uses `send`, so the second test may pass with no further change. If it does, say so and explain why.

**Refactor.** Move the `try/except` and the result-building into a private `_deliver(channel_name, channel, notification)` method. `send` then reads as: look up the channel, deliver. Tests stay green.

**Suggested commit messages.** `test: failed channel returns a failed result`, `feat: catch ChannelError in send`, `test: send_many continues after a failure`, then `refactor: extract _deliver`.

### Cycle 8: an unknown name in send\_many sends nothing (Boundary)

**Red.**

```python
def test_send_many_with_unknown_channel_sends_nothing(service, email_channel):
    with pytest.raises(UnknownChannelError):
        service.send_many(["email", "fax"], Notification(to="a@x.com", body="hi"))
    assert email_channel.sent == []
```

It fails because email is sent before `fax` is reached.

**Green.** Check all names first, then send.

**Refactor.** `send_many` now looks each channel up once, up front, with `_channel_for`, then calls `_deliver` directly. Nothing is looked up twice, and `send` and `send_many` share both helpers. Tests stay green.

**Suggested commit messages.** `test: send_many validates all names before sending`, `feat: validate channel names up front`, then `refactor: resolve each channel once`.

### Cycle 9: EmailChannel (Zero, One, Exceptional)

The routing is done. Now build the real channels, in `tests/test_channels.py`. Write these tests one at a time, each its own red and green, in this order:

```python
def test_new_email_channel_has_sent_nothing():
    assert EmailChannel().sent == []


def test_email_channel_records_a_message():
    channel = EmailChannel()
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    channel.send(n)
    assert channel.sent == [n]


@pytest.mark.parametrize("to", ["", "no-at-sign"])
def test_email_channel_rejects_bad_recipient(to):
    channel = EmailChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to=to, body="hi", subject="Hello"))
    assert channel.sent == []


def test_email_channel_rejects_empty_body():
    channel = EmailChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to="a@x.com", body="", subject="Hello"))
    assert channel.sent == []
```

**Green.** `EmailChannel` in `channels.py`, built up one test at a time. Also add the `Channel` protocol to `channels.py` now.

**Refactor.** Move the checks into a private `_validate(notification)` method, so `send` reads: validate, then record. Tests stay green.

**Suggested commit messages.** One `test:` and one `feat:` per test, then `refactor: extract _validate in EmailChannel`.

### Cycle 10: SmsChannel (Zero, One, Exceptional)

Same order as cycle 9. The tests:

```python
def test_new_sms_channel_has_sent_nothing():
    assert SmsChannel().sent == []


def test_sms_channel_records_a_message():
    channel = SmsChannel()
    n = Notification(to="+919876543210", body="hi")
    channel.send(n)
    assert channel.sent == [n]


@pytest.mark.parametrize("to", ["", "12345", "abcdefghij", "+1234567890123456"])
def test_sms_channel_rejects_bad_number(to):
    channel = SmsChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to=to, body="hi"))
    assert channel.sent == []


def test_sms_channel_rejects_empty_body():
    channel = SmsChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to="+919876543210", body=""))
    assert channel.sent == []
```

**Refactor.** `EmailChannel` and `SmsChannel` now share one shape: validate, then record. Extract a `_RecordingChannel` base class that owns `sent` and `send`, with each subclass supplying its own `_validate`. The empty-body check then lives once, in the base class. Tests stay green.

**Suggested commit messages.** One `test:` and one `feat:` per test, then `refactor: extract _RecordingChannel base class`.

### Cycle 11: end to end with the real channels (Simple scenario)

**Red.** In `tests/test_service.py`:

```python
def test_real_channels_end_to_end():
    email, sms = EmailChannel(), SmsChannel()
    service = NotificationService({"email": email, "sms": sms})
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    results = service.send_many(["email", "sms"], n)
    assert [r.ok for r in results] == [True, False]
    assert email.sent == [n]
    assert sms.sent == []
```

The email address is not a valid phone number, so SMS fails while email succeeds. This should pass with no production changes. Say so, and explain that it is a safety-net test, not a design-driving one.

**Suggested commit message.** `test: end-to-end with real channels`

### Cycle 12: final cleanup (Refactor)

This cycle adds no behavior, so it has no new test. With every test green, make these changes one small step at a time, running the full suite after each:

1. Read `service.py` and `channels.py` top to bottom. Rename anything unclear.
2. Remove dead code, unused imports and leftover placeholders.
3. Give every public class and method type hints and a one-line docstring.
4. Export `Notification`, `SendResult`, `NotificationService`, `EmailChannel`, `SmsChannel`, `ChannelError` and `UnknownChannelError` from `notifications/__init__.py`. Do not change any test imports.

**Suggested commit message.** `refactor: final cleanup and public exports`

### Cycle 13: add a new channel without touching existing code (Extension)

This proves the design. The brief asks for a new channel that needs no change to existing tests, and the service should need no change either. The new channel is a `PushChannel`, for push notifications to a phone. Its recipient is a device token, and the only rule is that the token cannot be empty.

**Red.** Create a new file, `tests/test_push_channel.py`:

```python
def test_new_push_channel_has_sent_nothing():
    assert PushChannel().sent == []


def test_push_channel_delivers_through_the_service():
    push = PushChannel()
    service = NotificationService({"push": push})
    n = Notification(to="device-token-123", body="hi")
    assert service.send("push", n).ok
    assert push.sent == [n]


def test_push_channel_rejects_empty_device_token():
    push = PushChannel()
    with pytest.raises(ChannelError):
        push.send(Notification(to="", body="hi"))
    assert push.sent == []
```

These follow ZOMBIES: Zero, then One, then Exceptional. Write them one at a time, in this order, each with its own red and green.

**Green.** Add `PushChannel` to `channels.py` as a subclass of `_RecordingChannel`. It only supplies its own `_validate`: the device token (`to`) must not be empty. Export it from `__init__.py`. Do not edit `service.py` or any existing test file.

**Proof.** Once the user has committed cycle 12, run the read-only commands `git status` and `git diff --stat`. They must list only `channels.py`, `__init__.py` and the new test file. `service.py` and the existing tests must not appear. Paste that output into the README.

**Suggested commit messages.** One `test:` and one `feat:` per test, such as `test: new push channel has sent nothing` and `feat: add PushChannel without changing the service`.

## Final step: README and checks

Write `README.md` with these parts:

1. What the service is and how to run the tests (`pip install pytest`, then `pytest`).
2. The design in a few lines: service, channels, results. Include how to add a new channel in three steps: write a class with `send`, raise `ChannelError` on failure, pass it into the service dict.
3. The decisions and assumptions listed under Design, so a reviewer sees nothing was guessed silently.
4. How ZOMBIES guided the test order: a short table mapping each cycle to its ZOMBIES letter.
5. The `git status` and `git diff --stat` output from cycle 13, as proof that adding `PushChannel` changed no existing code.
6. **Reflection:** where did writing the test first change the design? Claude Code may draft this from `NOTES.md`, but the user must rewrite it in their own words and only keep what they genuinely noticed.

**Before finishing, verify each success criterion from the brief**

| Criterion | Where it shows |
| --- | --- |
| Red, green, refactor without skipping | The suggested commits read test, feat, refactor in order |
| Next test chosen with ZOMBIES | Cycle order and the README table |
| Fixtures and parametrize | Fixtures in cycle 3. Parametrize in cycles 5, 9, 10 and 13. |
| Service built test-first | No production code before a failing test, in every cycle |
| TDD cycle visible in history | Prefixed commits after every step |
| Design extended without breaking tests | Cycle 13 adds a channel. `service.py` and old tests are untouched. |
| Refactoring is visible | Seven `refactor:` commits, in cycles 3, 5, 7, 8, 9, 10 and 12 |

Finally, run the whole suite once more and suggest the commit message `docs: README and notes`. The user commits.
