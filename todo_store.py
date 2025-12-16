import json
import os
import datetime

TODO_FILE = "todos.json"


def load_todos():
    """Loads all todos from persistent storage."""
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    """Saves todos to persistent storage."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)
