from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

from langgraph.graph import StateGraph, END

from graph.state import AgentState
from tools.llm_factory import make_llm
from tools.shared_resources import TavilyClient
from memory.vfs import vfs   # ✅ SINGLETON VFS

# =================================================
# External Clients
# =================================================
tavily = TavilyClient()

# =================================================
# Intent Detection
# =================================================
def is_todo_request(text: str) -> bool:
    keywords = ["todo", "to-do", "task", "plan", "schedule"]
    return any(k in text.lower() for k in keywords)

# =================================================
# ROUTER NODE (must return STATE)
# =================================================
@traceable(name="router")
def router_node(state: AgentState) -> AgentState:
    # Router node does NO logic
    # Routing logic lives in route_decision()
    return state

# =================================================
# ROUTING FUNCTION (returns STRING KEY)
# =================================================
def route_decision(state: AgentState) -> str:
    user_text = state["messages"][-1].content
    if is_todo_request(user_text):
        return "todo"
    return "web_search"

# =================================================
# GRAPH NODES
# =================================================

@traceable(name="web_search_node")
def web_search_node(state: AgentState) -> AgentState:
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

    # Persist search output
    vfs.write_file(
        file_name="search.txt",
        prompt=query,
        response=content
    )

    state["search_results"] = content
    state["messages"].append(AIMessage(content=content))
    return state


@traceable(name="summarizer_node")
def summarizer_node(state: AgentState) -> AgentState:
    llm = make_llm()

    content = state.get("search_results", "")

    # ❌ Remove links/sources
    if "Sources:" in content:
        content = content.split("Sources:")[0].strip()

    prompt = HumanMessage(
        content=(
            "Summarize the following clearly.\n"
            "- No links\n"
            "- No sources\n\n"
            f"{content}"
        )
    )

    response = llm.invoke([prompt])

    vfs.write_file(
        file_name="summary.txt",
        prompt=prompt.content,
        response=response.content
    )

    state["messages"].append(response)
    return state


@traceable(name="todo_node")
def todo_node(state: AgentState) -> AgentState:
    llm = make_llm()

    prompt = HumanMessage(
        content=(
            "Create a clean, actionable to-do list.\n"
            "Rules:\n"
            "- NO links\n"
            "- NO sources\n"
            "- Use time blocks if applicable\n\n"
            f"Request:\n{state['messages'][-1].content}"
        )
    )

    response = llm.invoke([prompt])

    vfs.write_file(
        file_name="todos.md",
        prompt=prompt.content,
        response=response.content
    )

    state["messages"].append(response)
    return state

# =================================================
# GRAPH DEFINITION
# =================================================

graph = StateGraph(AgentState)

# Nodes
graph.add_node("router", router_node)
graph.add_node("web_search", web_search_node)
graph.add_node("summarize", summarizer_node)
graph.add_node("todo", todo_node)

# Entry
graph.set_entry_point("router")

# Conditional Routing (✅ CORRECT)
graph.add_conditional_edges(
    "router",
    route_decision,   # MUST be callable
    {
        "web_search": "web_search",
        "todo": "todo"
    }
)

# Flow
graph.add_edge("web_search", "summarize")
graph.add_edge("summarize", END)
graph.add_edge("todo", END)

# =================================================
# COMPILE AGENT
# =================================================

SummarizationAgent = graph.compile()
