from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.web_search_graph import web_search_node
from graph.summarizer_graph import summary_node

def router(state: AgentState) -> str:
    query = state["messages"][-1].content.lower()
    if any(k in query for k in ["summarize", "summary", "explain", "lessons"]):
        return "summary"
    return "search"

def build_state_graph():
    graph = StateGraph(AgentState)

    graph.add_node("search", web_search_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("search")

    graph.add_conditional_edges(
        "search",
        router,
        {
            "search": END,
            "summary": "summary",
        },
    )

    graph.add_edge("summary", END)

    return graph.compile()
