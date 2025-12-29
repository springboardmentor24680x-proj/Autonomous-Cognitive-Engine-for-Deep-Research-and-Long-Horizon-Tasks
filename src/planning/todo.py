class TodoManager:
    def add(self, state, tasks):
        if "todos" not in state:
            state["todos"] = []
        state["todos"].extend(tasks)

    def list(self, state):
        return state.get("todos", [])

    def complete(self, state, idx):
        if 0 <= idx < len(state["todos"]):
            state["todos"][idx]["done"] = True
