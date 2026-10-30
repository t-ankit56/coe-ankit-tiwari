# Part 1 · Day 3 — Python Craft & Object-Oriented Design

**Date completed:** · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Names and explains context managers and decorators and generators and the MRO | | |
| Explains how the MRO resolves methods | | |
| Uses type hints well | | |
| Applies Strategy or Observer to a real refactor | Yes | [Exercise 1](#exercise-1-refactor-the-notification-service-to-observer) · [README](../code/part-1/day-03-notification-service-observer-refactor/README.md#observer) |
| Writes a working context manager | | |
| Writes self-explaining code | | |

## Key learnings

### Context managers

### Decorators

### Generators

### Method resolution order

### Type hints

### Strategy and Observer

### SOLID

### Self-explaining code

## Exercises

### Exercise 1: Refactor the notification service to Observer

The [Day 2 notification service](../code/part-1/day-02-notification-service/) was copied as a baseline (`40ff3fd`) and extended test-first, following my plan ([observer-refactor-plan.md](../code/part-1/day-03-notification-service-observer-refactor/observer-refactor-plan.md)). The service is now the subject: after every delivery attempt it tells each subscribed observer the notification and the same `SendResult` it returns. Observers are anything with `on_delivery(notification, result)` (the `Observer` protocol). Routing is unchanged, so the channels are still the Strategy and the observers only hear what happened. Code, decisions and an example observer are in the [README](../code/part-1/day-03-notification-service-observer-refactor/README.md#observer).

| Cycle | What the test pinned | ZOMBIES | Kind |
| --- | --- | --- | --- |
| O1 | An observer receives a successful delivery | One | Red, then green (`subscribe`, `_notify`) |
| O2 | An observer receives a failed delivery | One | Safety net |
| O3 | Every observer is told once per channel in `send_many` | Many | Safety net |
| O4 | An unknown channel notifies nobody | Boundary | Safety net |
| O5 | An unsubscribed observer is not told | Boundary | Red, then green (`unsubscribe`) |
| O6 | Unsubscribing an unknown observer raises | Boundary | Safety net |
| O7 | A failing observer doesn't break delivery | Exceptional | Red, green, then refactor |

The safety-net tests passed with no production change, because the earlier code already behaved that way, so they have a `test:` commit and no `feat:` commit.

```
$ git log --oneline 40ff3fd^..58190f8 -- code/part-1/day-03-notification-service-observer-refactor
58190f8 docs: README and notes for observer
ad8c943 refactor: document observer API and suppress observer errors
5c029d6 feat: isolate observer errors
c8a740a test: failing observer does not break delivery
c09f3ec test: unsubscribing unknown observer raises
8717ef3 feat: add unsubscribe
28e557a test: unsubscribed observer is not notified
e344701 test: unknown channel notifies no observers
b802673 test: observers notified once per channel
d55f7d2 test: observer receives failed delivery
836ea57 feat: add subscribe and notify observers
e03a535 test: observer receives successful delivery
1485993 chore: add FakeObserver test double
40ff3fd chore: scaffold day 03 and copy day 2 service as baseline
```

The 27 Day 2 tests stayed green throughout, and no existing test file changed. `tests/fakes.py` only gained the new `FakeObserver` class:

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

```
$ pytest -v tests/test_observers.py
tests/test_observers.py::test_observer_receives_successful_delivery PASSED [ 14%]
tests/test_observers.py::test_observer_receives_failed_delivery PASSED   [ 28%]
tests/test_observers.py::test_all_observers_notified_once_per_channel PASSED [ 42%]
tests/test_observers.py::test_unknown_channel_notifies_nobody PASSED     [ 57%]
tests/test_observers.py::test_unsubscribed_observer_is_not_notified PASSED [ 71%]
tests/test_observers.py::test_unsubscribing_unknown_observer_raises PASSED [ 85%]
tests/test_observers.py::test_failing_observer_does_not_break_delivery PASSED [100%]
============================== 7 passed in 0.02s ===============================

$ pytest -q
34 passed in 0.03s
```

The final `_notify` uses `contextlib.suppress`, so one broken observer can't stop delivery or the others:

```python
def _notify(self, notification: Notification, result: SendResult) -> None:
    """Tell every observer about one delivery; an observer's error never stops the others."""
    for observer in self._observers:
        with suppress(Exception):
            observer.on_delivery(notification, result)
```

### Exercise 2: Write a small context manager

## Reflection

*Which concepts did you already use without knowing their names?*

## AI use

## Open questions

## Changes after review

- None yet.
