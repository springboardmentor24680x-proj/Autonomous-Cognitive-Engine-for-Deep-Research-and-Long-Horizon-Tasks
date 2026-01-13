from typing import Dict, List

class VirtualFileSystem:
    def __init__(self):
        self._files: Dict[str, str] = {}

    def write_file(self, file_name: str, prompt: str, response: str):
        self._files[file_name] = f"PROMPT:\n{prompt}\n\nRESPONSE:\n{response}"

    def read_file(self, file_name: str) -> str:
        return self._files[file_name]

    def ls(self) -> List[str]:
        return list(self._files.keys())

    def clear(self):
        self._files.clear()

vfs = VirtualFileSystem()
