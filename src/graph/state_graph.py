# src/graph/state_graph.py
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

# Absolute imports
from graph.state import AgentState
from tools.llm_factory import make_llm
from memory.vfs import vfs
from tools.shared_resources import TavilyClient

# ---------------- External Clients ----------------
tavily = TavilyClient()

# ---------------- GRAPH NODES ----------------
@traceable(name="web_search_node")
def web_search_node(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    results = tavily.search(query=query, max_results=5, include_answer=True)
    answer = results.get("answer", "No answer found.")
    sources = results.get("results", [])

    sources_text = ""
    for r in sources:
        sources_text += f"- {r['title']}\n  {r['url']}\n\n"

    content = f"{answer}\n\nSources:\n{sources_text}"

    # Persist search results
    vfs.write_file("search.txt", query, content)

    state["search_results"] = content
    state["messages"].append(AIMessage(content=content))
    return state


@traceable(name="summarizer_node")
def summarizer_node(state: AgentState) -> AgentState:
    llm = make_llm()
    content_to_summarize = state.get("search_results") or state["messages"][-1].content
    prompt = HumanMessage(content=f"Summarize the following information:\n\n{content_to_summarize}")
    response = llm.invoke([prompt])
    vfs.write_file("summary.txt", prompt.content, response.content)
    state["messages"].append(response)
    return state


@traceable(name="research_node")
def research_node(state: AgentState) -> AgentState:
    llm = make_llm()
    prompt = HumanMessage(content=state["messages"][-1].content)
    response = llm.invoke([prompt])
    state["messages"].append(response)
    return state


# ---------------- GRAPH DEFINITION ----------------
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("web_search", web_search_node)
graph.add_node("summarize", summarizer_node)
graph.add_node("research", research_node)

graph.set_entry_point("web_search")
graph.add_edge("web_search", "summarize")
graph.add_edge("summarize", END)

# ---------------- COMPILE AGENT ----------------
SummarizationAgent = graph.compile()
