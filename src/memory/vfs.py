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

def append_memory(role: str, content: str):
    memory = load_memory()
    memory.append({"role": role, "content": content})
    save_memory(memory)

def clear_memory():
    save_memory([])
