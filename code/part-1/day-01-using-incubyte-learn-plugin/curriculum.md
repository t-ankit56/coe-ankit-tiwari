# CLI To-Do List Curriculum

## Tech Stack
Python 3 (standard library only: `argparse`, `json`, `pathlib`, `dataclasses`)

## Module 1: Setup and First Command
Goal: A runnable `todo.py` that parses subcommands.
- [x] Step 1.1: Create `todo.py` with an argparse parser and a working `--help`
- [x] Step 1.2: Add the `add`, `list`, and `done` subcommands (printing placeholders)
- [x] Step 1.3: Route each subcommand to its own handler function

## Module 2: Tasks and Storage
Goal: Tasks persist between runs in `tasks.json`.
- [x] Step 2.1: Model a task with a `@dataclass`
- [x] Step 2.2: Load and save tasks to `tasks.json`
- [x] Step 2.3: Make `add` and `list` use real storage

## Module 3: Completing Tasks and Polish
Goal: Mark tasks done and handle bad input gracefully.
- [x] Step 3.1: Implement `done <id>`
- [x] Step 3.2: Handle unknown IDs and a corrupted `tasks.json` with clear messages and exit codes
- [x] Step 3.3: Nicer `list` output (checkboxes, empty-list message)
- [x] Step 3.4: Wrap-up: a quick review of what you built
