from tavily import TavilyClient
from langchain_core.messages import AIMessage
from memory.vfs import vfs

tavily = TavilyClient()

def web_search_node(state):
    # Safety: ensure messages exist
    if not state.get("messages"):
        return state

    query = state["messages"][-1].content

    results = tavily.search(
        query=query,
        max_results=5,
        include_answer=True
    )

    answer = results.get("answer", "No answer found.")
    sources = results.get("results", [])

    sources_text = ""
    for r in sources:
        title = r.get("title", "No title")
        url = r.get("url", "")
        sources_text += f"- {title}\n  {url}\n\n"

    content = f"{answer}\n\nSources:\n{sources_text}"

    # Persist to VFS
    vfs.write_file("search.txt", query, content)

    # Update state
    state["search_results"] = content
    state["messages"].append(AIMessage(content=content))

    return state
