#main.py

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

from state import AgentState
from llm_factory import make_llm
from vfs_tools import VirtualFileSystem
from tavily import TavilyClient


# ---------------- VFS (shared instance) ----------------
vfs = VirtualFileSystem()


# ---------------- External Clients ----------------
tavily = TavilyClient()


# ---------------- GRAPH NODES ----------------

@traceable(name="web_search_node")
def web_search_node(state: AgentState) -> AgentState:
    """
    Performs a real web search using Tavily and stores results in VFS + state.
    """
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

    # Persist search results
    vfs.write_file("search.txt", query, content)

    # Update state
    state["search_results"] = content
    state["messages"].append(AIMessage(content=content))

    return state


@traceable(name="summarizer_node")
def summarizer_node(state: AgentState) -> AgentState:
    """
    Summarizes search results (or fallback content) using the LLM.
    """
    llm = make_llm()

    content_to_summarize = (
        state.get("search_results")
        or state["messages"][-1].content
    )

    prompt = HumanMessage(
        content=f"Summarize the following information:\n\n{content_to_summarize}"
    )

    response = llm.invoke([prompt])

    # Persist summary
    vfs.write_file("summary.txt", prompt.content, response.content)

    state["messages"].append(response)
    return state


@traceable(name="research_node")
def research_node(state: AgentState) -> AgentState:
    """
    Handles non-web research queries (fallback node).
    """
    llm = make_llm()

    prompt = HumanMessage(
        content=state["messages"][-1].content
    )

    response = llm.invoke([prompt])
    state["messages"].append_attach(response)

    return state


# ---------------- GRAPH DEFINITION ----------------

graph = StateGraph(AgentState)

graph.add_node("web_search", web_search_node)
graph.add_node("summarize", summarizer_node)
graph.add_node("research", research_node)

# Current flow: always do web search → summarize
graph.set_entry_point("web_search")
graph.add_edge("web_search", "summarize")
graph.add_edge("summarize", END)

# ---------------- COMPILE AGENT ----------------

SummarizationAgent = graph.compile()


# ---------------- LOCAL TEST ----------------

if __name__ == "__main__":
    initial_state = AgentState(
        messages=[HumanMessage(content="Latest Nvidia updates")]
    )

    final_state = SummarizationAgent.invoke(initial_state)

    print("=== SEARCH RESULTS ===")
    print(vfs.read_file("search.txt"))

    print("\n=== SUMMARY ===")
    print(vfs.read_file("summary.txt"))

