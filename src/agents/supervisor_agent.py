from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from memory.vfs import append_memory, load_memory
from mcp_server.client import call_mcp_sync

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

class SupervisorState(TypedDict):
    input: str
    plan: str
    search_result: str
    mcp_result: str
    response: str
    summary: str
    output: str

# ---------- NODES ----------

def planner_node(state: SupervisorState):
    res = llm.invoke(f"Create a short TODO plan to answer:\n{state['input']}")
    return {"plan": res.content}

def search_node(state: SupervisorState):
    result = SearchAgent.invoke({"query": state["input"]})
    return {"search_result": result["result"]}

def mcp_node(state: SupervisorState):
    enriched = call_mcp_sync(
        f"Plan:\n{state['plan']}\nSearch Result:\n{state['search_result']}"
    )
    return {"mcp_result": enriched}

def respond_node(state: SupervisorState):
    memory = load_memory()
    context = "\n".join([f"{m['role']}: {m['content']}" for m in memory[-6:]])

    prompt = f"""
You are a helpful AI.
IMPORTANT:
- Do NOT include a summary.
- Provide only the full detailed response.

Conversation Context:
{context}

Plan:
{state['plan']}

Search Info:
{state['search_result']}

MCP Enrichment:
{state['mcp_result']}

User:
{state['input']}

Assistant:
"""
    res = llm.invoke(prompt)

    return {
        "response": res.content
    }

def summarize_node(state: SupervisorState):
    summary = SummarizerAgent.invoke({
        "input": f"Summarize this in exactly 2 sentences:\n{state['response']}"
    })["output"]

    append_memory("user", state["input"])
    append_memory("assistant", state["response"], summary)

    return {
        "output": state["response"],
        "summary": summary
    }

# ---------- GRAPH ----------

graph = StateGraph(SupervisorState)

graph.add_node("planner", planner_node)
graph.add_node("search", search_node)
graph.add_node("mcp", mcp_node)
graph.add_node("respond", respond_node)
graph.add_node("summarize", summarize_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "search")
graph.add_edge("search", "mcp")
graph.add_edge("mcp", "respond")
graph.add_edge("respond", "summarize")
graph.add_edge("summarize", END)

SupervisorAgent = graph.compile()
