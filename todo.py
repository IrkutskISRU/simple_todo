import typer
import json
from pathlib import Path

app = typer.Typer()

BASE_DIR = Path(__file__).parent
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
        typer.echo("Неизвестное имя списка")
        raise typer.Exit(code=1)
    return list_name


def get_list_path(list_name: str) -> Path:
    return BASE_DIR / f".list_{list_name}"


def load_todos(list_name: str):
    path = get_list_path(list_name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


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
        status = "✅" if t.get("done") else "✔️ "
        typer.echo(f"{t['id']}. {status} {t['task']}")


def add_task(list_name: str, task: str):
    todos = load_todos(list_name)
    todos.append({"id": len(todos) + 1, "task": task, "done": False})
    renumber_todos(todos)
    save_todos(list_name, todos)
    typer.echo(f"[{list_name}] Задача добавлена: {task}")


def delete_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        removed = todos.pop(id - 1)
        renumber_todos(todos)
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Задача удалена: {removed['task']}")
    else:
        typer.echo("Неверный ID задачи")


def mark_done(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["done"] = True
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Задача {id} отмечена как выполненная")
    else:
        typer.echo("Неверный ID задачи")


def mark_undone(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["done"] = False
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Задача {id} снова помечена как невыполненная")
    else:
        typer.echo("Неверный ID задачи")


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


@app.command("move")
def move(src: str, dst: str, id: int):
    lists = load_lists()
    if src not in lists or dst not in lists:
        typer.echo("Неизвестное имя списка")
        raise typer.Exit(code=1)

    todos_src = load_todos(src)
    if not (0 < id <= len(todos_src)):
        typer.echo("Неверный ID задачи")
        raise typer.Exit(code=1)

    task = todos_src.pop(id - 1)
    renumber_todos(todos_src)
    save_todos(src, todos_src)

    todos_dst = load_todos(dst)
    todos_dst.append(task)
    renumber_todos(todos_dst)
    save_todos(dst, todos_dst)

    typer.echo(f"Задача '{task['task']}' перемещена из {src} в {dst}")


if __name__ == "__main__":
    ensure_lists_file()
    app()

