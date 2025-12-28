from typing import Dict, List
from pathlib import Path
from langsmith import traceable


class VirtualFileSystem:
    """
    In-memory + disk-backed virtual file system for agent memory.
    """

    def __init__(self, base_dir: str = "data/vfs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.files: Dict[str, str] = {}
        self.history: Dict[str, List[str]] = {}

    @traceable(name="vfs_write")
    def write_file(self, file_name: str, prompt: str, response: str):
        """
        Write a file to VFS and append to history.
        """
        entry = f"Prompt:\n{prompt}\n\nResponse:\n{response}\n\n---\n"

        self.history.setdefault(file_name, []).append(entry)
        self.files[file_name] = "".join(self.history[file_name])

        file_path = self.base_dir / file_name
        file_path.write_text(self.files[file_name], encoding="utf-8")

    @traceable(name="vfs_read")
    def read_file(self, file_name: str) -> str:
        """
        Read file content from VFS or disk.
        """
        if file_name in self.files:
            return self.files[file_name]

        file_path = self.base_dir / file_name
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            self.files[file_name] = content
            return content

        return ""

    def ls(self) -> List[str]:
        """
        List all files in VFS.
        """
        return list(self.files.keys())
