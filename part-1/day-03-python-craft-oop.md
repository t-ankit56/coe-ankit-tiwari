# Part 1 · Day 3 — Python Craft & Object-Oriented Design

**Date completed:** · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Names and explains context managers and decorators and generators and the MRO | | |
| Explains how the MRO resolves methods | | |
| Uses type hints well | | |
| Applies Strategy or Observer to a real refactor | Yes | [Exercise 1](#exercise-1-refactor-the-notification-service-to-observer) · [README](../code/part-1/day-03-notification-service-observer-refactor/README.md#observer) |
| Writes a working context manager | Yes | [Exercise 2](#exercise-2-write-a-small-context-manager) · [README](../code/part-1/day-03-context-manager/README.md) |
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

The final `_notify` uses `contextlib.suppress`, so one broken observer can't stop delivery or the others ([service.py](../code/part-1/day-03-notification-service-observer-refactor/src/notifications/service.py)).

### Exercise 2: Write a small context manager

`working_directory(path)` is a class-based context manager: `__enter__` saves the current directory, changes into `path` and returns it, and `__exit__` always changes back, even when the block raises. I'd use a context manager whenever something must be undone after a block, whatever happens in it: files, locks, transactions, or the working directory. The stdlib has the same thing as `contextlib.chdir`; this rebuilds it to show the protocol. Code, usage and how it works are in the [README](../code/part-1/day-03-context-manager/README.md).

| Cycle | What the test pinned | ZOMBIES | Kind |
| --- | --- | --- | --- |
| C1 | Inside the block, cwd is the target | One | Red, then green |
| C2 | After the block, cwd is restored | One | Red, green, then refactor (`target` fixture) |
| C3 | `as` gives the target path | One | Red, then green |
| C4 | An error in the block restores cwd and propagates | Exceptional | Safety net |
| C5 | A missing directory raises `FileNotFoundError`, cwd unchanged | Boundary | Safety net |

C4 and C5 passed as soon as they were written. `__exit__` runs however the block ends, and a failing `os.chdir` in `__enter__` means the block and `__exit__` never run, so neither needed new code.

```
$ git log --oneline 7a56dec^..468dcc7 -- code/part-1/day-03-context-manager
468dcc7 refactor: type hint exit parameters
4572ea5 test: missing directory raises and cwd is unchanged
2ba2d7f test: error in block restores cwd and propagates
e1b8786 feat: return target path from enter
6e39537 test: as gives the target path
c75e282 refactor: extract target fixture in tests
9212d81 feat: restore previous directory on exit
3440926 test: cwd is restored after block
1675105 feat: change into target directory on enter
7a56dec test: inside block cwd is the target directory
```

```
$ pytest -v
tests/test_working_directory.py::test_inside_block_cwd_is_target PASSED  [ 20%]
tests/test_working_directory.py::test_after_block_cwd_is_restored PASSED [ 40%]
tests/test_working_directory.py::test_as_gives_target_path PASSED        [ 60%]
tests/test_working_directory.py::test_error_in_block_restores_cwd_and_propagates PASSED [ 80%]
tests/test_working_directory.py::test_missing_directory_raises_and_cwd_is_unchanged PASSED [100%]
============================== 5 passed in 0.01s ===============================
```

## Reflection

*Which concepts did you already use without knowing their names?*

## AI use

## Open questions

## Changes after review

- None yet.
