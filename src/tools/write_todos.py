# src/tools/write_todos.py
from langsmith import traceable
from langchain_core.messages import AIMessage, HumanMessage
from graph.state import AgentState
from tools.llm_factory import make_llm
from memory.vfs import vfs

@traceable(name="todo_node")
def todo_node(state: AgentState) -> AgentState:
    """
    Create a to-do list from the last user message.
    Returns updated state with AIMessage.
    """
    if not state.get("messages"):
        return state

    llm = make_llm()
    user_input = state["messages"][-1].content

    prompt = HumanMessage(
        content=(
            "Create a clean, actionable to-do list.\n"
            "- NO links\n"
            "- NO sources\n"
            "- Use time blocks if applicable\n\n"
            f"Request:\n{user_input}"
        )
    )

    response = llm.invoke([prompt])

    # Save to VFS
    vfs.write_file(
        file_name="todos.md",
        prompt=prompt.content,
        response=response.content
    )

    # Append AIMessage
    new_state = dict(state)
    new_state["messages"].append(response)
    return new_state
