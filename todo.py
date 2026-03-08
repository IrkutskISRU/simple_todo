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
        typer.echo("Неизвестное имя списка")
        raise typer.Exit(code=1)
    return list_name


def get_list_path(list_name: str) -> Path:
    return BASE_DIR / f".list_{list_name}"


def load_todos(list_name: str):
    path = get_list_path(list_name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            todos = json.load(f)
            # Обеспечиваем наличие поля pinned у всех задач
            for t in todos:
                if "pinned" not in t:
                    t["pinned"] = False
            return todos
    return []

def pin_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["pinned"] = True
        # Перемещаем закреплённые задачи в начало списка
        pinned_tasks = [t for t in todos if t.get("pinned")]
        other_tasks = [t for t in todos if not t.get("pinned")]
        new_todos = pinned_tasks + other_tasks
        renumber_todos(new_todos)
        save_todos(list_name, new_todos)
        typer.echo(f"[{list_name}] Задача {id} закреплена")
    else:
        typer.echo("Неверный ID задачи")

def unpin_task(list_name: str, id: int):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        todos[id - 1]["pinned"] = False
        # После открепления сортируем: сначала все закреплённые, потом остальные
        pinned_tasks = [t for t in todos if t.get("pinned")]
        other_tasks = [t for t in todos if not t.get("pinned")]
        new_todos = pinned_tasks + other_tasks
        renumber_todos(new_todos)
        save_todos(list_name, new_todos)
        typer.echo(f"[{list_name}] Задача {id} откреплена")
    else:
        typer.echo("Неверный ID задачи")



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


def reset_list(list_name: str):
    todos = load_todos(list_name)
    changed = 0
    for t in todos:
        if t.get("done"):
            t["done"] = False
            changed += 1
    if changed:
        save_todos(list_name, todos)
    typer.echo(f"[{list_name}] Сброшено выполненных задач: {changed}")

def edit_task(list_name: str, id: int, new_task: str):
    todos = load_todos(list_name)
    if 0 < id <= len(todos):
        old_task = todos[id - 1]["task"]
        todos[id - 1]["task"] = new_task
        save_todos(list_name, todos)
        typer.echo(f"[{list_name}] Задача {id} отредактирована: '{old_task}' → '{new_task}'")
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


@app.command("reset")
def reset_cmd(list_name: str):
    list_name = ensure_list_name(list_name)
    reset_list(list_name)


@app.command("show")
def dash_cmd():
    """Показать дашборд по всем основным спискам."""
    script = BASE_DIR / "dashboard.sh"
    try:
        subprocess.run(["bash", str(script)], check=True)
    except FileNotFoundError:
        typer.echo("Файл dashboard.sh не найден рядом с todo.py")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Ошибка выполнения dashboard.sh (код {e.returncode})")

@app.command("edit")
def edit_cmd(list_name: str, id: int, new_task: str):
    """Редактировать текст задачи в указанном списке."""
    list_name = ensure_list_name(list_name)
    edit_task(list_name, id, new_task)

@app.command("priority")
def priority_cmd(list_name: str, from_id: int, to_id: int):
    """Установить приоритет задачи: переместить задачу с позиции from_id на позицию to_id."""
    list_name = ensure_list_name(list_name)
    set_priority(list_name, from_id, to_id)

@app.command("pin")
def pin_cmd(list_name: str, id: int):
    """Закрепить задачу в указанном списке."""
    list_name = ensure_list_name(list_name)
    pin_task(list_name, id)

@app.command("unpin")
def unpin_cmd(list_name: str, id: int):
    """Открепить задачу в указанном списке."""
    list_name = ensure_list_name(list_name)
    unpin_task(list_name, id)


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

def set_priority(list_name: str, from_id: int, to_id: int):
    todos = load_todos(list_name)
    n = len(todos)

    # Проверка корректности ID
    if not (1 <= from_id <= n) or not (1 <= to_id <= n):
        typer.echo("Неверный ID задачи")
        raise typer.Exit(code=1)

    # Преобразуем ID в индексы (от 0)
    from_idx = from_id - 1
    to_idx = to_id - 1

    # Извлекаем задачу, которую нужно переместить
    task_to_move = todos.pop(from_idx)

    # Вставляем задачу в новую позицию
    todos.insert(to_idx, task_to_move)

    # Перенумеровываем все задачи
    renumber_todos(todos)
    save_todos(list_name, todos)

    typer.echo(f"[{list_name}] Задача {from_id} перемещена на позицию {to_id}")



if __name__ == "__main__":
    ensure_lists_file()
    app()

