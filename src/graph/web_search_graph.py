import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.messages import AIMessage
from graph.state import AgentState
from memory.vfs import vfs

load_dotenv()

def web_search_node(state: AgentState) -> AgentState:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not found")

    tavily = TavilyClient(api_key=api_key)

    query = state["messages"][-1].content.strip()

    response = tavily.search(
        query=query,
        max_results=5,
        include_answer=False,
    )

    # ✅ Correct extraction
    results = response.get("results", [])

    formatted_blocks = []
    for r in results:
        formatted_blocks.append(
            f"TITLE: {r.get('title', 'N/A')}\n"
            f"URL: {r.get('url', 'N/A')}\n"
            f"CONTENT: {r.get('content', '')}\n"
        )

    combined = "\n\n".join(formatted_blocks)

    state["search_results"] = combined
    state.setdefault("messages", []).append(AIMessage(content=combined))

    vfs.write_file("search.txt", query, combined)
    return state
