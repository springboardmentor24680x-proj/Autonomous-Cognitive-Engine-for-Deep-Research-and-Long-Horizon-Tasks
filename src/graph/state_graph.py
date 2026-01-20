# src/graph/state_graph.py

from langgraph.graph import StateGraph, END
from graph.state import AgentState

from agents.planner_agent import planner_node
from agents.agents.research_agent import research_node
from agents.agents.summarizer_agent import summarizer_node


def build_graph():
    graph = StateGraph(AgentState)

    # ---------------- Nodes ----------------
    graph.add_node("planner", planner_node)
    graph.add_node("research", research_node)
    graph.add_node("summarizer", summarizer_node)

    # ------------- Entry Point -------------
    graph.set_entry_point("planner")

    # --------- Sequential Execution --------
    graph.add_edge("planner", "research")
    graph.add_edge("research", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()
