# tools/vfs_tools.py
from langchain_core.tools import tool
from typing import Dict

@tool
def ls(vfs: Dict) -> str:
    """List all files in the virtual file system."""
    return "\n".join(vfs["files"].keys()) if vfs.get("files") else "No files"

@tool
def read_file(filename: str, vfs: Dict) -> str:
    """Read the content of a file from the virtual file system."""
    return vfs.get("files", {}).get(filename, "File not found")

@tool
def write_file(filename: str, content: str, vfs: Dict) -> str:
    """Write content to a file in the virtual file system."""
    if "files" not in vfs:
        vfs["files"] = {}
    vfs["files"][filename] = content
    return f"{filename} saved"