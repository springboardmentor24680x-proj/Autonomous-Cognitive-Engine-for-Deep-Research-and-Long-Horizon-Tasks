from langsmith import traceable
@traceable(name="Edit_File_Tool")
def edit_vfs_file(state: dict, filename: str, new_content: str):
    """Appends content to an existing file in the state."""
    current = state["files"].get(filename, "")
    updated = current + "\n" + new_content
    state["files"][filename] = updated
    return state