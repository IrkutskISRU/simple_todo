import typer
import json
from pathlib import Path

app = typer.Typer()
TODO_FILE = Path.home() / ".todolist"

def load_todos():
    if TODO_FILE.exists():
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def renumber_todos(todos):
    for i, t in enumerate(todos, start=1):
        t["id"] = i

@app.command()
def add(task: str):
    todos = load_todos()
    todos.append({"id": len(todos) + 1, "task": task, "done": False})
    renumber_todos(todos)
    save_todos(todos)
    typer.echo(f"Задача добавлена: {task}")

@app.command()
def list():
    todos = load_todos()
    for t in todos:
        status = "✅" if t["done"] else "✔️ "
        typer.echo(f"{t['id']}. {status} {t['task']}")

@app.command()
def done(id: int):
    todos = load_todos()
    if 0 < id <= len(todos):
        todos[id - 1]["done"] = True
        save_todos(todos)
        typer.echo(f"Задача {id} отмечена как выполненная")
    else:
        typer.echo("Неверный ID задачи")

@app.command("del")
def delete(id: int):
    todos = load_todos()
    if 0 < id <= len(todos):
        removed = todos.pop(id - 1)
        renumber_todos(todos)
        save_todos(todos)
        typer.echo(f"Задача удалена: {removed['task']}")
    else:
        typer.echo("Неверный ID задачи")

if __name__ == "__main__":
    app()

