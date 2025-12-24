# tools/vfs_tools.py
from langchain_core.tools import tool

# -----------------------------
# LIST FILES
# -----------------------------
@tool
def ls(vfs: dict) -> str:
    """
    List all files stored in the virtual file system.
    """
    if not vfs:
        return "No files present."
    return "\n".join(vfs.keys())


# -----------------------------
# READ FILE
# -----------------------------
@tool
def read_file(filename: str, vfs: dict) -> str:
    """
    Read the content of a file from the virtual file system.
    """
    return vfs.get(filename, "File not found.")


# -----------------------------
# WRITE FILE
# -----------------------------
@tool
def write_file(filename: str, content: str, vfs: dict) -> str:
    """
    Create a new file and store content in the virtual file system.
    """
    vfs[filename] = content
    return f"File '{filename}' written successfully."


# -----------------------------
# EDIT FILE
# -----------------------------
@tool
def edit_file(filename: str, content: str, vfs: dict) -> str:
    """
    Edit an existing file in the virtual file system.
    """
    if filename not in vfs:
        return "File not found."
    vfs[filename] = content
    return f"File '{filename}' updated successfully."