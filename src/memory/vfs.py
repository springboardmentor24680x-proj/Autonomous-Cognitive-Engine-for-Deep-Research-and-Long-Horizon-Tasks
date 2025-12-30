# src/memory/vfs.py
from typing import Dict, List
from langsmith import traceable

class VirtualFileSystem:
    def __init__(self):
        self.files: Dict[str, str] = {}
        self.history: Dict[str, List[str]] = {}

    @traceable(name="vfs_write")
    def write_file(self, file_name: str, prompt: str, response: str):
        entry = f"Prompt:\n{prompt}\n\nResponse:\n{response}\n\n---\n"
        self.history.setdefault(file_name, []).append(entry)
        self.files[file_name] = "".join(self.history[file_name])
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(self.files[file_name])

    @traceable(name="vfs_read")
    def read_file(self, file_name: str) -> str:
        return self.files.get(file_name, "")

    def ls(self) -> list:
        return list(self.files.keys())

# ---- This is correct ----
# just create the singleton instance here
vfs = VirtualFileSystem()
