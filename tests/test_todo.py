from tools.write_todos import write_todos

def test_todo_generation():
    todos = write_todos("Create an AI research agent")

    assert isinstance(todos, list)
    assert len(todos) > 0
