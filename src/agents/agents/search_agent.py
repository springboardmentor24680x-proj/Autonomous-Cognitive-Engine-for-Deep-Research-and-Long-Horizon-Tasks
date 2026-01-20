# agents/search_agent.py
from graph.state import AgentState
from graph.web_search_graph import web_search_node

def search_agent(state: AgentState) -> AgentState:
    """
    Performs web search using web_search_node and updates state
    """
    state = web_search_node(state)
    return state
