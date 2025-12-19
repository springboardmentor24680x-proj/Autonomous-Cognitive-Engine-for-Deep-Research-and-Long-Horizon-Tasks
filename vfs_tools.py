# vfs.py
import os
from typing import Dict

class VirtualFileSystem:
    def __init__(self):
        self.files: Dict[str, str] = {}  # file_name -> content

    # Write or create a file
    def write_file(self, file_name: str, content: str):
        self.files[file_name] = content
        # Optional: also save to disk
        with open(file_name, "w") as f:
            f.write(content)

    # Read file content
    def read_file(self, file_name: str) -> str:
        return self.files.get(file_name, "")

    # Edit file content
    def edit_file(self, file_name: str, new_content: str):
        if file_name in self.files:
            self.files[file_name] = new_content
            # Optional: also save to disk
            with open(file_name, "w") as f:
                f.write(new_content)

    # List all files
    def ls(self) -> list:
        return list(self.files.keys())
