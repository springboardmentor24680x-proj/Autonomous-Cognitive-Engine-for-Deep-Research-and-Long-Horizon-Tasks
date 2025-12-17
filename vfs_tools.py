def ensure_files(state):
    state.setdefault("files", {})


def ls(state):
    return list(state["files"].keys())


def read(state, filename):
    return state["files"].get(filename, "File not found")


def write(state, filename, content):
    state["files"][filename] = content
    return f"Wrote to {filename}"


def edit(state, filename, content, mode="append"):
    if filename not in state["files"]:
        return "File not found"
    if mode == "overwrite":
        state["files"][filename] = content
    else:
        state["files"][filename] += "\n" + content
    return f"Edited {filename}"


def delete(state, filename):
    state["files"].pop(filename, None)
    return f"Deleted {filename}"


def clear(state, filename):
    state["files"][filename] = ""
    return f"Cleared {filename}"


def rename(state, old, new):
    state["files"][new] = state["files"].pop(old)
    return f"Renamed {old} → {new}"


def help_text():
    return (
        "VFS Commands:\n"
        "  ls\n"
        "  read <file>\n"
        "  write <file> <text>\n"
        "  edit <file> <text>\n"
        "  delete <file>\n"
    )
