from typing import Dict
from langsmith import traceable

class VFS:
    def __init__(self, files: Dict[str, str] | None = None):
        self.files = files or {}

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(files=data.copy())

    def to_dict(self) -> Dict[str, str]:
        return self.files.copy()

    # NOT traced – used by UI
    def ls(self):
        return list(self.files.keys())

    # Traced ONLY when called by agent
    @traceable(name="vfs_read", run_type="tool")
    def _read_traced(self, filename: str) -> str:
        return self.files.get(filename, "")

    def read_file(self, filename: str, traced: bool = False) -> str:
        if traced:
            return self._read_traced(filename)
        return self.files.get(filename, "")

    @traceable(name="vfs_write", run_type="tool")
    def write_file(self, filename: str, content: str):
        self.files[filename] = content

    @traceable(name="vfs_edit", run_type="tool")
    def edit_file(self, filename: str, content: str):
        self.files[filename] = content
