from langgraph.graph import StateGraph, END
from typing import TypedDict

class SearchState(TypedDict):
    query: str
    result: str

def search_node(state: SearchState):
    # This acts as a specialist. In production, use TavilySearchResults here.
    return {"result": "FACT: Narendra Modi is the Prime Minister of India. Dr. APJ Abdul Kalam was the 11th President."}

graph = StateGraph(SearchState)
graph.add_node("search", search_node)
graph.set_entry_point("search")
graph.add_edge("search", END)
WebSearchAgent = graph.compile()