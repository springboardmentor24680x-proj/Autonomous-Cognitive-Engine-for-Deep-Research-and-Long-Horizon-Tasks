from tavily import TavilyClient
from langchain_core.messages import AIMessage
from memory.vfs import vfs

tavily = TavilyClient()

def web_search_node(state):
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
        sources_text += f"- {r['title']}\n  {r['url']}\n\n"

    content = f"{answer}\n\nSources:\n{sources_text}"

    vfs.write_file("search.txt", query, content)

    state["search_results"] = content
    state["messages"].append(AIMessage(content=content))

    return state
