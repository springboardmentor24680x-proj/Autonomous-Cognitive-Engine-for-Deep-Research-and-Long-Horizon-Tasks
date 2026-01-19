def file_manager(action: str, state: dict, filename: str, content: str = ""):
    if action == "write":
        state["files"][filename] = content
    elif action == "read":
        return state["files"].get(filename, "File not found")
    elif action == "edit":
        state["files"][filename] = state["files"].get(filename, "") + f"\n{content}"
    return state