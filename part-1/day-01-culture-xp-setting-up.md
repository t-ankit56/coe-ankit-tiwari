# Part 1 · Day 1 — Incubyte Culture XP & Setting Up to Build

**Date completed:** 2026-10-28 · **Time spent:** ~6 hrs

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Understands Incubyte's pod model and values in action | Yes | [section](#independent-pod-and-values-in-action) |
| Names the guiding principle that will stretch them most and why | Yes | [section](#the-principle-that-will-stretch-me) |
| Explains the core XP practices | Yes | [section](#extreme-programming) |
| Explains the four DORA metrics | Yes | [section](#dora-metrics) |
| Installs Claude Code with BEE and Learn and runs Learn on a task | Yes | [code](../code/part-1/day-01-using-incubyte-learn-plugin/) · [section](#exercise-1-learn-plugin-on-a-small-task) |
| Has a working Python project with pytest and Git | Yes | [code](../code/part-1/day-01-python-pytest-setup/) · [section](#exercise-2-python-project-with-pytest) |
| Reflects on what is new in XP | Yes | [section](#reflection) |

## Key learnings

### Independent Pod and Values in Action

An independent pod is a self-sufficient team that owns a client product end to end without being dependent on other teams. Values in action are the values and guiding principles that a pod uses to guide them while working on projects. For example extreme ownership means taking ownership of the project and completing the backlog tasks even when no one has assigned it to you.

### The principle that will stretch me

The principle of Relentless Pursuit of Quality with Pragmatism is the one that feels most challenging to me. Most of the things such as TDD, CI/CD, code reviews etc. were not followed by me in my past jobs. So making sure that I follow them every time I build something will stretch me, but I will happily do that.

### Extreme Programming

Extreme Programming is a methodology where we follow practices like pair programming, TDD, CI/CD, refactoring guided by the principles such as simplicity, communication, feedback, courage and respect. After going through these I understood that Incubyte guiding principles are also highly influenced by extreme programming practices and I will make sure to follow these while working.  

### DORA metrics

DORA metrics are used to show the throughput of software changes and also the instability of software changes. Throughput can be measured by change lead time, deployment frequency and failed deployment recovery time. Instability can be measured by change fail rate and deployment rework rate. Together these can be used to understand a team's software delivery performance.

## Exercises

### Exercise 1: Learn plugin on a small task

Installed Claude Code and the Incubyte BEE and Learn plugins, then ran Learn to build a small command-line to-do list in Python (standard library only).

```
$ claude --version
2.1.311 (Claude Code)
$ claude plugin list
Installed plugins:
  ❯ bee@incubyte-plugins
    Version: 0.6.0
    Scope: user
    Status: ✔ enabled
  ❯ learn@incubyte-plugins
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled
```

Learn generated a three-module curriculum ([curriculum.md](../code/part-1/day-01-using-incubyte-learn-plugin/curriculum.md)): setup and first command, tasks and storage, then completing tasks and polish. I completed all ten steps. The result is [todo.py](../code/part-1/day-01-using-incubyte-learn-plugin/todo.py), with `add`, `list` and `done` commands. Tasks are saved to `tasks.json`, and an unknown ID or a corrupted file gives a clear error and exit code 1.

```
$ python todo.py list
No tasks yet. Add one with: todo add "Buy milk"
$ python todo.py add "Buy milk"
Added task #1: Buy milk
$ python todo.py add "Walk dog"
Added task #2: Walk dog
$ python todo.py done 1
Completed task #1: Buy milk
$ python todo.py list
[x] 1. Buy milk
[ ] 2. Walk dog
$ python todo.py done 42
todo: error: no task with ID 42. Run 'todo list' to see your tasks.
$ echo $?
1
```

`tasks.json` is created at runtime, so it's in `.gitignore` and not committed.

### Exercise 2: Python project with pytest

Set up a separate project: [day-01-python-pytest-setup](../code/part-1/day-01-python-pytest-setup/). It has:

- a virtual environment (`venv/`, ignored by Git)
- pytest pinned in `requirements.txt`
- a `pyproject.toml` that points pytest at `tests/` and adds the project folder to the import path, so `from calculator import add` works from `tests/`
- one test for a small `add` function

How to set it up and run it: [README](../code/part-1/day-01-python-pytest-setup/README.md).

```
$ pytest -v
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
configfile: pyproject.toml
testpaths: tests
collected 1 item

tests/test_calculator.py::test_add PASSED                                [100%]

============================== 1 passed in 0.01s ===============================
```

Git history for this part:

```
8700a51 docs: add setup and test instruction for pytest project
7fbbb0f feat: add add() with a pytest test
a720dc5 chore: set up python project with pytest
8ba9423 chore: ignore venv folder
```

Problems along the way:
- `python3 -m venv` first failed because `ensurepip` was missing. Installing `python3.14-venv` fixed it.
- Without the `pythonpath` setting, pytest only adds `tests/` to the import path, so importing the module from the project root can fail.

## Reflection

Till now, I have been working as a software developer who built features solo, and the major thing I missed was advice from peers on improving my coding practices. Pair programming, an XP practice, will be the biggest change for me, along with giving and receiving feedback regularly. Going forward I'll ask for reviews early instead of only when a feature is done.

## AI use

- **Claude Code + Learn plugin:** guided me through building the to-do CLI step by step ([curriculum](../code/part-1/day-01-using-incubyte-learn-plugin/curriculum.md)).
- **Claude Code as a reviewer:**
  - checked my repo layout, commits and Git identity against the submission guidelines
  - explained `pyproject.toml`, pytest's import path behaviour, and one venv per project vs one shared venv
- **Claude Code wrote:**
  - `.gitignore`
  - `pyproject.toml`
  - `calculator.py` and its test
  - the pytest project README
  - the first draft of this file's criteria table and Exercises section
- **What I corrected:**
  - Claude first put the pytest setup inside the to-do project. I pointed out that these are two separate criteria, so they are now separate projects.
  - Its first test module was a parametrized file-name generator with error cases. I had it replaced with a simple `add(1, 1) == 2` test, because the criterion is only a working pytest setup.

## Open questions

- Is one virtual environment per project the expected setup in this COE?

## Changes after review

- None yet.
