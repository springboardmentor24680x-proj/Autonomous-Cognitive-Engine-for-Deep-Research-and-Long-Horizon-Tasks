from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import supervisor, execute_task, final_synthesis


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("execute", execute_task)
    graph.add_node("final", final_synthesis)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["action"],
        {
            "execute": "execute",
            "finish": "final"
        }
    )

    graph.add_edge("execute", "supervisor")
    graph.add_edge("final", END)

    return graph.compile()