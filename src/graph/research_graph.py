# src/graph/research_graph.py
from graph.state import AgentState
from graph.web_search_graph import web_search_node
from graph.summarizer_graph import summary_node

def research_node(state: AgentState) -> AgentState:
    """
    Performs both web search (Tavily) and summarization (OpenRouter)
    """
    state = web_search_node(state)
    state = summary_node(state)
    return state
