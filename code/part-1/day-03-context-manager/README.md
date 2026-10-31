# Day 3 — Context manager

`working_directory(path)`: a class-based context manager that changes into `path` for the length of a `with` block, and always changes back afterwards, even when the block raises. Built test-first with pytest.

## Setup

```bash
cd code/part-1/day-03-context-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test

```bash
pytest -v
```

5 tests in `tests/test_working_directory.py`. A `target` fixture moves each test into its own `tmp_path`, so a test can never leave the process in another directory.

## Usage

```python
from working_directory import working_directory

with working_directory("build") as path:
    ...  # cwd is build/, path is its absolute Path
# cwd is back to where it was
```

## How it works

- `__enter__` saves `Path.cwd()`, changes into `path`, and returns the new cwd. That return value is what `as` binds.
- `__exit__` changes back to the saved directory. Python calls it however the block ends, so the restore happens even on an error.
- `__exit__` returns `None` (falsy), so an exception from the block is never swallowed.
- If `path` doesn't exist, `os.chdir` raises `FileNotFoundError` inside `__enter__`. Python then never runs the block or `__exit__`, and cwd is unchanged.

## When to use one

Use one whenever something has to be undone after a block of code, whether the block succeeds or fails: closing a file, releasing a lock, rolling back a transaction, or putting the working directory back. The `with` statement makes forgetting the cleanup impossible, and the setup and cleanup sit together in one place instead of in a `try`/`finally` at every caller.

The standard library already has this one: `contextlib.chdir` (Python 3.11+). This exercise rebuilds it to show the protocol.

## Cycle order (ZOMBIES)

| Cycle | What the test pinned | ZOMBIES | Kind |
| --- | --- | --- | --- |
| C1 | Inside the block, cwd is the target | One | Red, then green (`__enter__` changes dir) |
| C2 | After the block, cwd is restored | One | Red, then green (`__exit__` restores), then refactor (`target` fixture) |
| C3 | `as` gives the target path | One | Red, then green (`__enter__` returns `Path`) |
| C4 | An error in the block restores cwd and propagates | Exceptional | Safety net (passed at once) |
| C5 | A missing directory raises `FileNotFoundError`, cwd unchanged | Boundary | Safety net |
| — | Type hints on `__exit__` parameters | — | Refactor |
