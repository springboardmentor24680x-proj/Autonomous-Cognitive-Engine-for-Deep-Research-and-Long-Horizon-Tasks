# tests/test_todo.py
from langchain_core.messages import HumanMessage
from graph.state_graph import todo_node

def test_todo_node_generation():
    state = {"messages": [HumanMessage(content="Create a todo list for AI project")]}
    output_state = todo_node(state)

    last_msg = output_state["messages"][-1]
    from langchain_core.messages import AIMessage
    assert isinstance(last_msg, AIMessage)
    assert "todo" in last_msg.content.lower() or len(last_msg.content) > 0
