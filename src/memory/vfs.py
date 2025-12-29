class VFS:
    def _ensure(self, state):
        if "files" not in state:
            state["files"] = {}

    def ls(self, state):
        self._ensure(state)
        return list(state["files"].keys())

    def read(self, state, name):
        self._ensure(state)
        return state["files"].get(name, "❌ File not found")

    def write(self, state, name, content):
        self._ensure(state)
        state["files"][name] = content
        return f"✅ Written file: {name}"

    def edit(self, state, name, content):
        self._ensure(state)
        if name not in state["files"]:
            return "❌ File not found"
        state["files"][name] = content
        return f"✏️ Updated file: {name}"
