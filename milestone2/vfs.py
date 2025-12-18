# tools/vfs_tools.py
from langchain.tools import tool

@tool
def ls(state=None):
    """List files in the Virtual File System."""
    return list(state.get("vfs", {}).keys())

@tool
def read_file(args=None, state=None):
    """Read a file from VFS."""
    args = args or {}
    filename = args.get("filename")
    if not filename:
        return "Error: filename required."

    vfs = state.get("vfs", {})
    if filename not in vfs:
        return f"File '{filename}' not found."

    return vfs[filename]

@tool
def write_file(args=None, state=None):
    """Write/overwrite file in VFS."""
    args = args or {}
    filename = args.get("filename")
    content = args.get("content", "")

    if not filename:
        return "Error: filename required."

    state.setdefault("vfs", {})[filename] = content
    return f"Written to '{filename}'."

@tool
def edit_file(args=None, state=None):
    """Append content to VFS file."""
    args = args or {}
    filename = args.get("filename")
    content = args.get("content", "")

    if not filename:
        return "Error: filename required."

    vfs = state.setdefault("vfs", {})
    if filename not in vfs:
        vfs[filename] = content
        return f"File '{filename}' created."

    vfs[filename] += "\n" + content
    return f"Appended to '{filename}'."