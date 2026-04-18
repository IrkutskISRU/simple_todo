#!/usr/bin/env python3

import typer
import json
import subprocess
from pathlib import Path

app = typer.Typer()

BASE_DIR = Path(__file__).resolve().parent
LISTS_FILE = BASE_DIR / "lists.txt"
DEFAULT_LISTS = ["yesterday", "today", "tomorrow", "pool", "trash"]


def ensure_lists_file():
    if not LISTS_FILE.exists():
        LISTS_FILE.write_text("\n".join(DEFAULT_LISTS) + "\n", encoding="utf-8")


def load_lists():
    ensure_lists_file()
    content = LISTS_FILE.read_text(encoding="utf-8")
    return [line.strip() for line in content.splitlines() if line.strip()]


def ensure_list_name(list_name: str) -> str:
    lists = load_lists()
    if list_name not in lists:
        typer.echo("Unknown list name")
        raise typer.Exit(code=1)
    return list_name


def get_list_path(list_name: str) -> Path:
    return BASE_DIR / f".list_{list_name}"


def load_todos(list_name: str):
    path = get_list_path(list_name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            todos = json.load(f)
            # Ensure all tasks have a pinned field
            for t in todos:
                if "pinned" not in t:
                    t["pinned"] = False
            return todos
    return []

def pin_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["pinned"] = True
        # Move pinned tasks to the beginning of the list
        pinned_tasks = [t for t in todos if t.get("pinned")]
        other_tasks = [t for t in todos if not t.get("pinned")]
        new_todos = pinned_tasks + other_tasks
        renumber_todos(new_todos)
        save_todos(list_name, new_todos)
        typer.echo(f"[{list_name}] Task {id} pinned")
    else:
        typer.echo("Invalid task ID")

def unpin_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["pinned"] = False
        # After unpinning, keep pinned tasks first, then the rest
        pinned_tasks = [t for t in todos if t.get("pinned")]
        other_tasks = [t for t in todos if not t.get("pinned")]
        new_todos = pinned_tasks + other_tasks
        renumber_todos(new_todos)
        save_todos(list_name, new_todos)
        typer.echo(f"[{list_name}] Task {id} unpinned")
    else:
        typer.echo("Invalid task ID")



def save_todos(list_name: str, todos):
    path = get_list_path(list_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)


def renumber_todos(todos):
    for i, t in enumerate(todos, start=1):
        t["id"] = i


def list_tasks(list_name: str):
    todos = load_todos(list_name)
    for t in todos:
        status = "✅ " if t.get("done") else "✔️ "
        pin_symbol = "📌 " if t.get("pinned") else ""
        typer.echo(f"{t['id']}. {pin_symbol}{status} {t['task']}")



def add_task(list_name: str, task: str):
    todos = load_todos(list_name)
    todos.append({"id": len(todos) + 1, "task": task, "done": False})
    renumber_todos(todos)
    save_todos(list_name, todos)
    typer.echo(f"[{list_name}] Task added: {task}")


def delete_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        removed = todos.pop(id - 1)
        renumber_todos(todos)
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Task deleted: {removed['task']}")
    else:
        typer.echo("Invalid task ID")


def mark_done(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["done"] = True
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Task {id} marked as done")
    else:
        typer.echo("Invalid task ID")


def mark_undone(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["done"] = False
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Task {id} marked as not done again")
    else:
        typer.echo("Invalid task ID")


def reset_list(list_name: str):
    todos = load_todos(list_name)
    changed = 0
    for t in todos:
        if t.get("done"):
            t["done"] = False
            changed += 1
    if changed:
        save_todos(list_name, todos)
    typer.echo(f"[{list_name}] Completed tasks reset: {changed}")

def edit_task(list_name: str, id: int, new_task: str):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        old_task = todos[id - 1]["task"]
        todos[id - 1]["task"] = new_task
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Task {id} edited: '{old_task}' -> '{new_task}'")
    else:
        typer.echo("Invalid task ID")


@app.command("list")
def list_cmd(list_name: str):
    list_name = ensure_list_name(list_name)
    list_tasks(list_name)


@app.command("add")
def add_cmd(list_name: str, task: str):
    list_name = ensure_list_name(list_name)
    add_task(list_name, task)


@app.command("del")
def del_cmd(list_name: str, id: int):
    list_name = ensure_list_name(list_name)
    delete_task(list_name, id)


@app.command("do")
def do_cmd(list_name: str, id: int):
    list_name = ensure_list_name(list_name)
    mark_done(list_name, id)


@app.command("undo")
def undo_cmd(list_name: str, id: int):
    list_name = ensure_list_name(list_name)
    mark_undone(list_name, id)


@app.command("reset")
def reset_cmd(list_name: str):
    list_name = ensure_list_name(list_name)
    reset_list(list_name)


@app.command("show")
def dash_cmd():
    """Show a dashboard for all main lists."""
    script = BASE_DIR / "dashboard.sh"
    try:
        subprocess.run(["bash", str(script)], check=True)
    except FileNotFoundError:
        typer.echo("dashboard.sh not found next to todo.py")
    except subprocess.CalledProcessError as e:
        typer.echo(f"dashboard.sh execution error (code {e.returncode})")

@app.command("edit")
def edit_cmd(list_name: str, id: int, new_task: str):
    """Edit task text in the specified list."""
    list_name = ensure_list_name(list_name)
    edit_task(list_name, id, new_task)

@app.command("priority")
def priority_cmd(list_name: str, from_id: int, to_id: int):
    """Set task priority: move a task from position from_id to position to_id."""
    list_name = ensure_list_name(list_name)
    set_priority(list_name, from_id, to_id)

@app.command("pin")
def pin_cmd(list_name: str, id: int):
    """Pin a task in the specified list."""
    list_name = ensure_list_name(list_name)
    pin_task(list_name, id)

@app.command("unpin")
def unpin_cmd(list_name: str, id: int):
    """Unpin a task in the specified list."""
    list_name = ensure_list_name(list_name)
    unpin_task(list_name, id)


@app.command("move")
def move(
    src: str,
    dst: str,
    id: int = typer.Argument(None),
    all: bool = typer.Option(False, "--all", help="Move all tasks from src to dst"),
):
    lists = load_lists()
    if src not in lists or dst not in lists:
        typer.echo("Unknown list name")
        raise typer.Exit(code=1)
    todos_src = load_todos(src)
    todos_dst = load_todos(dst)
    if all:
        if not todos_src:
            typer.echo(f"[{src}] No tasks to move")
            return
        moved_count = len(todos_src)
        todos_dst.extend(todos_src)
        todos_src = []
        renumber_todos(todos_src)
        renumber_todos(todos_dst)
        save_todos(src, todos_src)
        save_todos(dst, todos_dst)
        typer.echo(f"Moved tasks: {moved_count} from {src} to {dst}")
        return
    # old behavior: move one task by id
    if id is None:
        typer.echo("Specify a task ID or use --all")
        raise typer.Exit(code=1)
    if not (0 < id <= len(todos_src)):
        typer.echo("Invalid task ID")
        raise typer.Exit(code=1)
    task = todos_src.pop(id - 1)
    renumber_todos(todos_src)
    save_todos(src, todos_src)
    todos_dst.append(task)
    renumber_todos(todos_dst)
    save_todos(dst, todos_dst)
    typer.echo(f"Task '{task['task']}' moved from {src} to {dst}")

def set_priority(list_name: str, from_id: int, to_id: int):
    todos = load_todos(list_name)
    n = len(todos)

    # Validate ID range
    if not (1 <= from_id <= n) or not (1 <= to_id <= n):
        typer.echo("Invalid task ID")
        raise typer.Exit(code=1)

    # Convert IDs to zero-based indices
    from_idx = from_id - 1
    to_idx = to_id - 1

    # Extract task to move
    task_to_move = todos.pop(from_idx)

    # Insert task into the new position
    todos.insert(to_idx, task_to_move)

    # Renumber all tasks
    renumber_todos(todos)
    save_todos(list_name, todos)

    typer.echo(f"[{list_name}] Task {from_id} moved to position {to_id}")



if __name__ == "__main__":
    ensure_lists_file()
    app()

