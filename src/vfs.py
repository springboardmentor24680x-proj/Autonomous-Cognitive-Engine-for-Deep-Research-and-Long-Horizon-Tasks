# vfs.py
from typing import Dict, List

class VFS:
    """
    Simple dynamic Virtual File System.
    Fully serializable via dict (for LangGraph MemorySaver).
    """

    def __init__(self, files: Dict[str, str] = None):
        self.files: Dict[str, str] = files if files is not None else {}

    def ls(self) -> List[str]:
        return list(self.files.keys())

    def read_file(self, filename: str) -> str:
        return self.files.get(filename, "")

    def write_file(self, filename: str, content: str) -> str:
        self.files[filename] = content
        return f"[vfs] wrote '{filename}' ({len(content)} chars)"

    def edit_file(self, filename: str, new_content: str) -> str:
        if filename in self.files:
            self.files[filename] += "\n" + new_content
            return f"[vfs] appended to '{filename}'"
        else:
            self.files[filename] = new_content
            return f"[vfs] created '{filename}' (via edit)"

    def delete_file(self, filename: str) -> str:
        if filename in self.files:
            del self.files[filename]
            return f"[vfs] deleted '{filename}'"
        return f"[vfs] '{filename}' not found"

    def dump(self) -> Dict[str, str]:
        return dict(self.files)

    # Serialize / deserialize for LangGraph
    def to_dict(self) -> Dict[str, str]:
        return dict(self.files)

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(files=data)
