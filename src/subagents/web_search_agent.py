import os
from typing import TypedDict
from langgraph.graph import StateGraph
from langsmith import traceable
import groq
from tavily import TavilyClient
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Missing API keys")

client = groq.Client(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# ---------------- STATE ----------------
class WebState(TypedDict):
    query: str
    result: str

# ---------------- LLM (optional reasoning) ----------------
@traceable(name="Web_Search_LLM", run_type="llm")
def web_search_llm(query: str) -> str:
    """
    Optional: Use LLM to summarize or refine web search results.
    """
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a research assistant. Answer factually."},
            {"role": "user", "content": query}
        ],
        max_tokens=700
    )
    return resp.choices[0].message.content.strip()

# ---------------- NODE ----------------
@traceable(name="Web_Search_Node", run_type="chain")
def web_node(state: WebState) -> WebState:
    """
    Uses Tavily to fetch live results + optional LLM summarization
    """
    try:
        response = tavily_client.search(query=state["query"], max_results=5, include_answer=True)
        urls = [item.get("url", "") for item in response.get("results", [])]
        result_text = ""
        for item in response.get("results", []):
            result_text += f"- {item.get('title','')} : {item.get('snippet','')}\n"
        result_text += "\n[Source URLs: " + ", ".join(urls) + "]"

        # Optional: Refine via LLM
        # result_text = web_search_llm(result_text)

        state["result"] = result_text or "[No results found]"
    except Exception as e:
        state["result"] = f"[Web search failed: {e}]"
    return state

# ---------------- GRAPH ----------------
graph = StateGraph(WebState)
graph.add_node("search", web_node)
graph.add_edge("__start__", "search")
graph.add_edge("search", "__end__")

web_agent_app = graph.compile()
