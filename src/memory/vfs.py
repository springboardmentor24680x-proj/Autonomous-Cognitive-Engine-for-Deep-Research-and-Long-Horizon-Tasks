from langchain_core.tools import tool
import streamlit as st

# Use session_state so the files don't disappear when the app refreshes
if "VFS" not in st.session_state:
    st.session_state["VFS"] = {}

VFS = st.session_state["VFS"]
# ----------------------------
# In-memory VFS
# ----------------------------
def normalize_filename(filename: str) -> str:
    return filename.lstrip("/")

def clear_vfs():
    """Clears all files from the VFS memory."""
    global VFS
    VFS.clear()

# if "VFS" not in st.session_state:
#     st.session_state["VFS"] = {}

# VFS = st.session_state["VFS"]

def write_file(filename: str, content: str) -> str:
    """
    Appends content to a file in the VFS.
    """
    filename = normalize_filename(filename)
    if filename in VFS:
        VFS[filename] += "\n" + content
    else:
        VFS[filename] = content
    return f"Todo saved in {filename}"


def read_file(filename: str) -> str:
    """Reads and returns the content of the file from the VFS. Input: filename (str)."""
    filename = normalize_filename(filename)
    if filename in VFS:
        return VFS[filename]
    return f"File '{filename}' not found."

def edit_file(filename: str, new_content: str) -> str:
    """Updates the content of an existing file in the VFS. Inputs: filename (str), new_content (str)."""
    filename = normalize_filename(filename)
    if filename not in VFS:
        return f"File '{filename}' does not exist."
    VFS[filename] = new_content
    return f"File '{filename}' updated."

def ls(*args, **kwargs) -> list:  # Change return type to list
    """Returns a list of filenames for the MCP server to handle."""
    return list(VFS.keys())

def delete_file(filename: str) -> str:
    """Removes a file from the Virtual File System."""
    clean_name = filename.lstrip('/')
    if clean_name in VFS:
        del VFS[clean_name]
        return f"SUCCESS: {clean_name} has been deleted."
    return f"ERROR: File {clean_name} not found."
