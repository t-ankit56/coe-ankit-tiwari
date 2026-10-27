import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

TASKS_FILE = Path("tasks.json")

@dataclass
class Task:
    id: int
    title: str
    is_done: bool = False


class TodoError(Exception):
    pass


def load_tasks() -> list[Task]:
    if not TASKS_FILE.exists():
        return []
    try:
        raw_tasks = json.loads(TASKS_FILE.read_text())
        return [Task(**raw_task) for raw_task in raw_tasks]
    except (json.JSONDecodeError, TypeError) as error:
        raise TodoError(
            f"{TASKS_FILE} is corrupted ({error}). Fix it or delete it to start fresh."
        ) from error


def save_tasks(tasks: list[Task]) -> None:
    raw_tasks = [asdict(task) for task in tasks]
    TASKS_FILE.write_text(json.dumps(raw_tasks, indent=2))

def next_task_id(tasks: list[Task]) -> int:
    return max((task.id for task in tasks), default=0) + 1


def add_task(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    task = Task(id=next_task_id(tasks), title=args.title)
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task.id}: {task.title}")


def format_task(task: Task) -> str:
    checkbox = "[x]" if task.is_done else "[ ]"
    return f"{checkbox} {task.id}. {task.title}"


def list_tasks(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    if not tasks:
        print('No tasks yet. Add one with: todo add "Buy milk"')
        return
    for task in tasks:
        print(format_task(task))


def complete_task(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    for task in tasks:
        if task.id == args.task_id:
            task.is_done = True
            save_tasks(tasks)
            print(f"Completed task #{task.id}: {task.title}")
            return
    raise TodoError(f"no task with ID {args.task_id}. Run 'todo list' to see your tasks.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A tiny command-line to-do list.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_command = commands.add_parser("add", help="add a new task")
    add_command.add_argument("title", help="what needs doing")
    add_command.set_defaults(handler=add_task)

    list_command = commands.add_parser("list", help="show all tasks")
    list_command.set_defaults(handler=list_tasks)

    done_command = commands.add_parser("done", help="mark a task as complete")
    done_command.add_argument("task_id", type=int, help="ID of the task to complete")
    done_command.set_defaults(handler=complete_task)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except TodoError as error:
        print(f"todo: error: {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()