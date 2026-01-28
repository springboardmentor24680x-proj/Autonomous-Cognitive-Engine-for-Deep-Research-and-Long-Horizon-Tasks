from langgraph.graph import StateGraph
from agents.supervisor import supervisor
from agents.summarizer import summarizer_node

def build_state_graph():
    graph = StateGraph(dict)

    graph.add_node("supervisor", supervisor)
    graph.add_node("summarizer", summarizer_node)

    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "summarizer")
    graph.set_finish_point("summarizer")

    return graph.compile()
