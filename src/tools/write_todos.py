from typing import List

def write_todos(todo_list: List[str], filename: str = "todo_list.txt"):
    """Writes the current todo list to a string format for the VFS."""
    content = "\n".join([f"- {item}" for item in todo_list])
    return filename, content