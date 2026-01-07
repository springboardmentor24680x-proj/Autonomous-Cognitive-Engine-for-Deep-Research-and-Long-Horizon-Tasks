import json
import os

VFS_PATH = "memory_store.json"

def load_memory():
    if not os.path.exists(VFS_PATH):
        return []
    with open(VFS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(VFS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_memory(role: str, content: str, summary: str | None = None):
    memory = load_memory()
    entry = {
        "role": role,
        "content": content
    }
    if summary:
        entry["summary"] = summary
    memory.append(entry)
    save_memory(memory)

def clear_memory():
    save_memory([])
