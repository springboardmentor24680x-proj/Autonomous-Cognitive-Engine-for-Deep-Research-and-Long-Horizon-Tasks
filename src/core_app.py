# src/core_app.py
from langchain_core.messages import HumanMessage
from langsmith import traceable

from graph.state_graph import SummarizationAgent
from graph.state import AgentState
from memory.vfs import VirtualFileSystem

vfs = VirtualFileSystem()

@traceable(name="chat_turn")
def run_agent(state: AgentState):
    """
    Core agent execution logic (NO Streamlit)
    """
    return SummarizationAgent.invoke(state)


def create_initial_state():
    """
    Creates a fresh AgentState
    """
    return AgentState(
        messages=[],
        search_results=None,
        next_node=None
    )


def invoke_chat(state: AgentState, user_input: str) -> AgentState:
    """
    Single chat turn – used by Streamlit and pytest
    """
    state["messages"].append(HumanMessage(content=user_input))
    return run_agent(state)
