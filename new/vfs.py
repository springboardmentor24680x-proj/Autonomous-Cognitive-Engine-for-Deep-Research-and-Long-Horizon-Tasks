
class VFS:
    def ls(self, state):
        return list(state["files"].keys())

    def read(self, state, name):
        return state["files"].get(name, "❌ File not found")

    def write(self, state, name, content):
        state["files"][name] = content
        return f" Written file: {name}"

    def edit(self, state, name, content):
        if name not in state["files"]:
            return " File not found"
        state["files"][name] = content
        return f" Updated file: {name}"


vfs = VFS()
