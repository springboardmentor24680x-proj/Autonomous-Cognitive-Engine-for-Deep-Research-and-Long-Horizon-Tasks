# src/agents/search_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from tools.search_tool import web_search

class SearchState(TypedDict):
    query: str
    result: str

def search_node(state: SearchState):
    return {"result": web_search.invoke(state["query"])}

graph = StateGraph(SearchState)
graph.add_node("search", search_node)
graph.set_entry_point("search")
graph.add_edge("search", END)

SearchAgent = graph.compile()
