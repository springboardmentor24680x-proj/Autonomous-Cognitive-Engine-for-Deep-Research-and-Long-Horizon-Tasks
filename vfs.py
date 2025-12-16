# ----------------------------
# In-memory VFS
# ----------------------------
VFS = {}

def clear_vfs():
    """Clears all files from the VFS memory."""
    global VFS
    VFS = {}

def write_file(filename: str, content: str) -> str:
    """
    Appends content to a file in the VFS.
    """
    if filename in VFS:
        VFS[filename] += "\n" + content
    else:
        VFS[filename] = content
    return f"Todo saved in {filename}"


def read_file(filename: str) -> str:
    """Reads and returns the content of the file from the VFS. Input: filename (str)."""
    if filename in VFS:
        return VFS[filename]
    return f"File '{filename}' not found."

def edit_file(filename: str, new_content: str) -> str:
    """Updates the content of an existing file in the VFS. Inputs: filename (str), new_content (str)."""
    if filename not in VFS:
        return f"File '{filename}' does not exist."
    VFS[filename] = new_content
    return f"File '{filename}' updated."

def ls(*args, **kwargs) -> str:  
    """Lists all file names currently stored in the VFS."""
    if not VFS:
        return "No files in VFS."
    return "Files: " + ", ".join(VFS.keys())
