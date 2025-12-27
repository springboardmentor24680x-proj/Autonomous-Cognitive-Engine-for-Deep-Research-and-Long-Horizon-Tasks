from src.main.app import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import read_file, clear_vfs

def setup_function():
    clear_vfs()

def test_todo_create_and_update():
    agent = setup_agent()

    # Match the prompt rules: Ask to create a WORK todo
    agent.invoke([
        HumanMessage(content="Create a work todo list with the task: Market research")
    ])

    # Match the prompt rules: Ask to add to WORK todos
    agent.invoke([
        HumanMessage(content="Add task: Competitor analysis to my work todos")
    ])

    # The tool will have created "todos_work.txt"
    todos = read_file("todos_work.txt")
    assert "Market research" in todos
    assert "Competitor analysis" in todos
