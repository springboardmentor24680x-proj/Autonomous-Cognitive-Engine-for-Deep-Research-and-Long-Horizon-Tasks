from langchain_core.tools import tool
import streamlit as st

# --------------------------------------------------
# Virtual File System (Persistent via session_state)
# --------------------------------------------------

if "VFS" not in st.session_state:
    st.session_state["VFS"] = {}

VFS = st.session_state["VFS"]


def normalize_filename(filename: str) -> str:
    return filename.lstrip("/")


@tool
def clear_vfs() -> str:
    """Clears all files from the virtual file system."""
    VFS.clear()
    return "VFS cleared successfully."


@tool
def write_file(filename: str, content: str) -> str:
    """
    Write or append content to a file in the VFS.
    """
    filename = normalize_filename(filename)

    if filename in VFS:
        VFS[filename] += "\n" + content
    else:
        VFS[filename] = content

    return f"File '{filename}' written successfully."


@tool
def read_file(filename: str) -> str:
    """
    Read a file from the VFS.
    """
    filename = normalize_filename(filename)

    if filename not in VFS:
        return f"ERROR: File '{filename}' not found."

    return VFS[filename]


@tool
def edit_file(filename: str, new_content: str) -> str:
    """
    Replace the content of an existing file.
    """
    filename = normalize_filename(filename)

    if filename not in VFS:
        return f"ERROR: File '{filename}' does not exist."

    VFS[filename] = new_content
    return f"File '{filename}' updated successfully."


@tool
def delete_file(filename: str) -> str:
    """
    Delete a file from the VFS.
    """
    filename = normalize_filename(filename)

    if filename not in VFS:
        return f"ERROR: File '{filename}' not found."

    del VFS[filename]
    return f"File '{filename}' deleted successfully."


@tool
def ls() -> list:
    """
    List all files in the VFS.
    Returns a list for tool compatibility.
    """
    return list(VFS.keys())
