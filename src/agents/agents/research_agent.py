# src/agents/agents/research_agent.py

from graph.state import AgentState
from memory.vfs import vfs

def research_agent(state: AgentState) -> AgentState:
    todo = state["current_todo"]["task"]

    vfs.write_file(
        file_name="research_notes.txt",
        prompt=todo,
        response=f"Notes collected for: {todo}"
    )

    return state
