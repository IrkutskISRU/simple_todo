# todo (CLI)

Minimal CLI todo manager built with [Typer](https://typer.tiangolo.com/).

Tasks are stored as JSON files per list in the project directory.

## Requirements

- Python 3
- `pip`
- Bash (only for `todo show`)

## Installation

### 1) Install dependency

```bash
python3 -m pip install --user typer
```

### 2) Run from the project folder

```bash
python3 todo.py --help
python3 todo.py list today
```

### 3) (Optional) Make it available as `todo`

The recommended way is to symlink `todo.py` into a directory that is in your `PATH`.

Example with `~/bin`:

```bash
mkdir -p ~/bin
ln -s /ABS/PATH/TO/PROJECT/todo.py ~/bin/todo
```

Ensure `~/bin` is in your `PATH` (zsh):

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Check:

```bash
which todo
todo --help
```

## Data files

All files are stored next to `todo.py` (the script resolves symlinks).

- `lists.txt`: list names (one per line)
- `.list_<name>`: tasks for a given list (JSON), e.g. `.list_today`, `.list_trash`

If a list name is not present in `lists.txt`, commands will fail with “Unknown list name”.

Default lists (created on first run if `lists.txt` is missing):

- `yesterday`
- `today`
- `tomorrow`
- `pool`
- `trash`

## Commands

### Show tasks

```bash
todo list <list>
```

Example:

```bash
todo list today
```

### Add a task

```bash
todo add <list> "task text"
```

Example:

```bash
todo add today "Buy milk"
```

### Delete a task by ID

```bash
todo del <list> <id>
```

Example:

```bash
todo del today 3
```

### Mark task as done

```bash
todo do <list> <id>
```

Example:

```bash
todo do today 1
```

### Mark task as NOT done (undo)

```bash
todo undo <list> <id>
```

Example:

```bash
todo undo today 1
```

### Reset all done tasks in a list

Marks all completed tasks in the given list as not completed.

```bash
todo reset <list>
```

Example:

```bash
todo reset daily
```

### Move a task between lists

```bash
todo move <src_list> <dst_list> <id>
```

Example:

```bash
todo move today yesterday 5
```

### Dashboard

Runs `dashboard.sh` which prints several lists in one screen.

```bash
todo show
```

You can also run it directly:

```bash
bash dashboard.sh
```

