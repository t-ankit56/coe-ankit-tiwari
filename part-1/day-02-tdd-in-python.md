# Part 1 · Day 2 — TDD in Python

**Date completed:** 2026-10-29 · **Time spent:** ~7 hours

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Follows red-green-refactor without skipping steps | Yes | [Exercise 2](#exercise-2-commit-after-every-green-and-refactor-step) · [section](#red-green-refactor) |
| Chooses the next test using ZOMBIES | Yes | [Exercise 1](#exercise-1-notification-service-test-first) · [README table](../code/part-1/day-02-notification-service/README.md#test-order-zombies) · [section](#zombies) |
| Uses pytest fixtures and parametrize | Yes | [conftest.py](../code/part-1/day-02-notification-service/tests/conftest.py) · [test_service.py](../code/part-1/day-02-notification-service/tests/test_service.py) · [test_channels.py](../code/part-1/day-02-notification-service/tests/test_channels.py) · [section](#pytest-essentials) |
| Builds a service test-first | Yes | [code](../code/part-1/day-02-notification-service/) · [Exercise 1](#exercise-1-notification-service-test-first) |
| Shows the TDD cycle in commit history | Yes | [Exercise 2](#exercise-2-commit-after-every-green-and-refactor-step) |
| Extends the design without breaking existing tests | Yes | [Exercise 3](#exercise-3-add-a-new-channel-without-changing-existing-tests) |

## Key learnings

### The Three Laws of TDD

The three laws of TDD say: don't write any production code until a failing test asks for it. Stop writing the test as soon as it fails; compilation errors such as an import error also count as a failure. Write only enough production code to make the failing test pass. In my service, `send` used the email channel by default until the SMS test was added; that test failed, and proper routing by channel name had to be added.

### Red-green-refactor

Red proves that a test can fail. The green is the simplest code used to pass the test, and refactor cleans up while ensuring the tests keep passing. Writing the test first makes you decide how the service will be used before writing code.

### ZOMBIES

ZOMBIES stands for Zero, One, Many, Boundary, Interface, Exceptional, Simple. It helps us pick tests in an order, so that we start with the simplest test and increase complexity step by step.

### pytest essentials

- Fixtures help remove repeated setup. When several tests use the same setup, it can be moved into a fixture, and any test can use it as a parameter.
- Parametrize runs one test over several inputs and reports each one separately. For example, to test several wrongly formatted phone numbers we can use parametrize.
- `assert` checks a condition, and if it fails pytest shows the difference in output, while `pytest.raises` checks that an error is raised.

## Exercises

### Exercise 1: Notification service test-first

A small `NotificationService` that routes a `Notification` to email, SMS or push channels by name and returns a `SendResult` per channel. Every channel has the same interface: `send(notification)`, raising `ChannelError` when it can't deliver. Nothing is really sent; channels record messages in memory. Setup, design and decisions: [README](../code/part-1/day-02-notification-service/README.md).

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

```
$ pytest -v
platform linux
tests/test_channels.py::test_new_email_channel_has_sent_nothing PASSED   [  3%]
tests/test_channels.py::test_email_channel_records_a_message PASSED      [  7%]
tests/test_channels.py::test_email_channel_rejects_bad_recipient[] PASSED [ 11%]
tests/test_channels.py::test_email_channel_rejects_bad_recipient[no-at-sign] PASSED [ 14%]
tests/test_channels.py::test_email_channel_rejects_empty_body PASSED     [ 18%]
tests/test_channels.py::test_new_sms_channel_has_sent_nothing PASSED     [ 22%]
tests/test_channels.py::test_sms_channel_records_a_message PASSED        [ 25%]
tests/test_channels.py::test_sms_channel_rejects_bad_number[] PASSED     [ 29%]
tests/test_channels.py::test_sms_channel_rejects_bad_number[12345] PASSED [ 33%]
tests/test_channels.py::test_sms_channel_rejects_bad_number[abcdefghij] PASSED [ 37%]
tests/test_channels.py::test_sms_channel_rejects_bad_number[+1234567890123456] PASSED [ 40%]
tests/test_channels.py::test_sms_channel_rejects_empty_body PASSED       [ 44%]
tests/test_push_channel.py::test_new_push_channel_has_sent_nothing PASSED [ 48%]
tests/test_push_channel.py::test_push_channel_delivers_through_the_service PASSED [ 51%]
tests/test_push_channel.py::test_push_channel_rejects_empty_device_token PASSED [ 55%]
tests/test_service.py::test_new_service_has_sent_nothing PASSED          [ 59%]
tests/test_service.py::test_send_via_email_reaches_only_email_channel PASSED [ 62%]
tests/test_service.py::test_send_via_sms_reaches_only_sms_channel PASSED [ 66%]
tests/test_service.py::test_send_returns_successful_result PASSED        [ 70%]
tests/test_service.py::test_unknown_channel_raises[fax] PASSED           [ 74%]
tests/test_service.py::test_unknown_channel_raises[] PASSED              [ 77%]
tests/test_service.py::test_unknown_channel_raises[EMAIL] PASSED         [ 81%]
tests/test_service.py::test_send_many_delivers_once_per_channel_in_order PASSED [ 85%]
tests/test_service.py::test_failed_channel_gives_failed_result PASSED    [ 88%]
tests/test_service.py::test_send_many_continues_after_a_failure PASSED   [ 92%]
tests/test_service.py::test_send_many_with_unknown_channel_sends_nothing PASSED [ 96%]
tests/test_service.py::test_real_channels_end_to_end PASSED              [100%]
============================== 27 passed in 0.05s ==============================
```

### Exercise 2: Commit after every green and refactor step

Every red, green and refactor step is its own commit (`test:`, `feat:`, `refactor:`), with 7 `refactor:` commits. Three `test:` commits passed on the first run, so no `feat:` follows them: `fbbcd95` (`send_many` already reused `send`, which caught the failure), `3f4159d` (end-to-end safety net) and `fe99c71` (`PushChannel` inherited `send`, and the service accepts any channel).

```
$ git log --oneline -- code/part-1/day-02-notification-service
7b6f788 docs: describe design and test order in README
a9c4ba4 feat: PushChannel rejects empty device token
dc30ef3 test: push channel rejects empty device token
fe99c71 test: push channel delivers through the service
f2692c6 feat: add PushChannel without changing the service
4917e3d test: new push channel has sent nothing
f5fcfa3 refactor: final cleanup and public exports
3f4159d test: end-to-end with real channels
999310f refactor: extract _RecordingChannel base class
d85edec feat: SmsChannel rejects empty body
acefbc1 test: sms channel rejects empty body
6a3c5c0 feat: SmsChannel rejects invalid numbers
b1e3e8c test: sms channel rejects bad number
f910aee feat: SmsChannel records sent messages
0428f12 test: sms channel records a message
bc239b1 feat: add SmsChannel
3fde4fe test: new sms channel has sent nothing
261718c refactor: extract _validate in EmailChannel
5674f40 feat: EmailChannel rejects empty body
ae23b92 test: email channel rejects empty body
23b1c03 feat: EmailChannel rejects recipients without @
d33486c test: email channel rejects bad recipient
4586340 feat: EmailChannel records sent messages
3a3e242 test: email channel records a message
1430c87 feat: add EmailChannel
4df7d51 test: new email channel has sent nothing
69c19ea refactor: resolve each channel once
16c4ea5 feat: validate channel names up front
90f4548 test: send_many validates all names before sending
218c7c9 refactor: extract _deliver
fbbcd95 test: send_many continues after a failure
8e307b3 feat: catch ChannelError in send
065e6ac test: failed channel returns a failed result
381ece8 feat: add send_many
47d8c98 test: send_many reaches every channel in order
8eacc40 refactor: extract _channel_for
e41b4d8 feat: reject unknown channels
cc70ca9 test: unknown channel names raise
95705b6 feat: send returns SendResult
253e70e test: send returns a successful result
25f8f63 refactor: extract FakeChannel and fixtures
24ecccc feat: route by channel name
9011900 test: send via sms reaches only sms channel
838d9db feat: send routes to the email channel
5a530e1 test: send via email reaches only email channel
2cd42f0 feat: NotificationService accepts channels
d81b4b0 test: new service has sent nothing
05fa77a chore: project skeleton with pytest config
```

### Exercise 3: Add a new channel without changing existing tests

Added `PushChannel`, which subclasses `_RecordingChannel` and adds only one rule: the device token must not be empty. `service.py` and every existing test file are unchanged; the "delivers through the service" test passed with no new code. Diff from the cleanup commit to the last push commit:

```
$ git diff --stat f5fcfa3..a9c4ba4 -- code/part-1/day-02-notification-service
 .../src/notifications/__init__.py                   |  3 ++-
 .../src/notifications/channels.py                   |  9 +++++++++
 .../tests/test_push_channel.py                      | 21 +++++++++++++++++++++
 3 files changed, 32 insertions(+), 1 deletion(-)
```

```
$ git diff f5fcfa3..a9c4ba4 -- code/part-1/day-02-notification-service/tests
diff --git a/code/part-1/day-02-notification-service/tests/test_push_channel.py b/code/part-1/day-02-notification-service/tests/test_push_channel.py
new file mode 100644
index 0000000..7d84a2f
--- /dev/null
+++ b/code/part-1/day-02-notification-service/tests/test_push_channel.py
@@ -0,0 +1,21 @@
+import pytest
+from notifications import ChannelError, Notification, NotificationService, PushChannel
+
+
+def test_new_push_channel_has_sent_nothing():
+    assert PushChannel().sent == []
+
+
+def test_push_channel_delivers_through_the_service():
+    push = PushChannel()
+    service = NotificationService({"push": push})
+    n = Notification(to="device-token-123", body="hi")
+    assert service.send("push", n).ok
+    assert push.sent == [n]
+
+
+def test_push_channel_rejects_empty_device_token():
+    push = PushChannel()
+    with pytest.raises(ChannelError):
+        push.send(Notification(to="", body="hi"))
+    assert push.sent == []
```

## Reflection

Before this, I used to build first and test manually later, which resulted in a lot of debugging and production hotfixes. By designing the service test-first, it became very easy to add a new notification channel at the end, because the service receives its channels instead of creating them; otherwise that might have required a lot of changes. Testing also helps with separation of concerns. The notification service is tested using a `FakeChannel`, and every channel is tested separately, which makes the service easier to manage later.

## AI use

- **Claude Code:** built the notification service with me one cycle at a time from my plan ([notification-service-plan.md](../code/part-1/day-02-notification-service/notification-service-plan.md)). I approved each step and made every commit.
- **Claude Code:** reviewed this file against the criteria, filled in the exercise output, fixed grammar in my Key learnings and Reflection.
- **What I corrected:** Claude suggested my reflection say the tests changed the design. I pushed back, because the design was mostly decided in the plan before the first test, so the reflection now only claims what actually happened. I also kept my own Key learnings content instead of adding the examples it suggested.

## Open questions

- Q.1 I did Interface (cycle 4) before Many (cycle 6), and Boundary (cycle 8) after Exceptional. How strictly should ZOMBIES be followed? Is it an order or a checklist?
- Q.2 My design was mostly fixed in the plan before the first test, so the tests confirmed it more than shaped it. On a real project, how much design should you do before starting TDD?

## Changes after review

- None yet.
