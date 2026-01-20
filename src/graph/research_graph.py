from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.planner_agent import planner_agent

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_agent)
    graph.set_entry_point("planner")
    graph.add_edge("planner", END)
    return graph.compile()
