# from typing import TypedDict, List, Dict, Any

# class AgentState(TypedDict):
#     messages: List[Dict[str, str]]
#     todos: List[Dict[str, Any]]
#     files: Dict[str, str]
#     current_task: str
# from langgraph.graph import StateGraph, END
# from src.agents.supervisor_agent import agent_step

# def supervisor_node(state: dict) -> dict:
#     """
#     One reasoning step of the supervisor
#     """
#     user_input = state.get("current_task", "")
#     return agent_step(user_input, state)


# def should_continue(state: dict) -> str:
#     """
#     Loop condition: continue if any TODO is not done
#     """
#     for t in state.get("todos", []):
#         if not t.get("done"):
#             return "continue"
#     return "end"


# def build_graph():
#     graph = StateGraph(dict)

#     graph.add_node("supervisor", supervisor_node)

#     graph.set_entry_point("supervisor")

#     graph.add_conditional_edges(
#         "supervisor",
#         should_continue,
#         {
#             "continue": "supervisor",
#             "end": END
#         }
#     )

#     return graph.compile()

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from src.agents.supervisor_agent import agent_step


# -------------------------------------------------
# SUPERVISOR NODE
# -------------------------------------------------
def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    One autonomous reasoning step
    """
    user_input = state.get("current_task", "")
    return agent_step(user_input, state)


# -------------------------------------------------
# LOOP CONDITION
# -------------------------------------------------
def should_continue(state: Dict[str, Any]) -> str:
    """
    Continue looping if any TODO is not done
    """
    for t in state.get("todos", []):
        if not t.get("done", False):
            return "continue"
    return "end"


# -------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------
def build_graph():
    graph = StateGraph(dict)

    graph.add_node("supervisor", supervisor_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "continue": "supervisor",
            "end": END
        }
    )

    return graph.compile()
