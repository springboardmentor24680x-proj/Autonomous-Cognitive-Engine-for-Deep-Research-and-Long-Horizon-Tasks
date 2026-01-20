# graph/web_search_graph.py
from graph.state import AgentState
from tools.llm_factory import make_llm

def web_search_node(state: AgentState) -> AgentState:
    query = state.get("query")
    if not query:
        state["search_results"] = ""
        return state

    # Using Tavily API for search
    search_client = make_llm(provider="tavily")
    results = search_client.search(query)  # replace with actual API method
    # Combine results into string
    content = "\n".join([r.get("snippet", "") for r in results])
    state["search_results"] = content
    return state
