
# class TodoManager:
#     def __init__(self):
#         self.todos = []

#     def add(self, tasks):
#         self.todos.extend(tasks)

#     def list(self):
#         return self.todos

#     def complete(self, idx):
#         if 0 <= idx < len(self.todos):
#             self.todos[idx]["done"] = True


# todo_manager = TodoManager()
class TodoManager:
    def add(self, state, tasks):
        state["todos"].extend(tasks)

    def list(self, state):
        return state["todos"]

    def complete(self, state, idx):
        if 0 <= idx < len(state["todos"]):
            state["todos"][idx]["done"] = True


todo_manager = TodoManager()
