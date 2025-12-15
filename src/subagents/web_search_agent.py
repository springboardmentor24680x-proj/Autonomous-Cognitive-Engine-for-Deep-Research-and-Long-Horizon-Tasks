from typing import TypedDict
from langgraph.graph import StateGraph
from tavily import TavilyClient
import os

class WebSearchState(TypedDict):
    query: str
    results: str

def web_search(state: WebSearchState):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=state["query"],
        max_results=5,
        include_answer=True
    )

    formatted = []
    for r in response.get("results", []):
        formatted.append(f"- {r['title']}\n{r['content']}\nSource: {r['url']}")

    state["results"] = "\n\n".join(formatted)
    return state

graph = StateGraph(WebSearchState)
graph.add_node("search", web_search)
graph.add_edge("__start__", "search")
graph.add_edge("search", "__end__")

web_search_agent = graph.compile()
