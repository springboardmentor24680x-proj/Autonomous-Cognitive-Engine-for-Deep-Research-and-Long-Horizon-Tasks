from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from vfs_tools import VirtualFileSystem

# ---------------- ENV ----------------
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# ---------------- STATE ----------------
class AgentState(TypedDict):
    messages: List[Any]

vfs = VirtualFileSystem()

# ---------------- LLM FACTORY ----------------
def make_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

# ---------------- SUPERVISOR ----------------
def supervisor(state: AgentState) -> AgentState:
    text = state["messages"][-1].content.lower()

    # Determine next node and store it in state
    if "summarize" in text:
        state["next_node"] = "summarizer"
    elif "research" in text or "explain" in text:
        state["next_node"] = "research"
    elif "code" in text or "program" in text:
        state["next_node"] = "code"
    elif "search" in text or "find" in text:
        state["next_node"] = "search"
    else:
        state["next_node"] = "research"

    return state

# ---------------- AGENT NODES ----------------
def summarizer_node(state: AgentState) -> AgentState:
    llm = make_llm()
    response = llm.invoke(state["messages"])

    last_prompt = state["messages"][-1].content
    vfs.write_file("summary.txt", last_prompt, response.content)

    state["messages"].append(response)
    return state

def research_node(state: AgentState) -> AgentState:
    llm = make_llm()
    response = llm.invoke(state["messages"])

    last_prompt = state["messages"][-1].content
    vfs.write_file("research.txt", last_prompt, response.content)

    state["messages"].append(response)
    return state

def code_node(state: AgentState) -> AgentState:
    llm = make_llm()
    response = llm.invoke(state["messages"])

    last_prompt = state["messages"][-1].content
    vfs.write_file("code.py", last_prompt, response.content)

    state["messages"].append(response)
    return state

def search_node(state: AgentState) -> AgentState:
    llm = make_llm()
    response = llm.invoke(state["messages"])

    last_prompt = state["messages"][-1].content
    vfs.write_file("search.txt", last_prompt, response.content)

    state["messages"].append(response)
    return state

# ---------------- GRAPH ----------------
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor)
graph.add_node("summarizer", summarizer_node)
graph.add_node("research", research_node)
graph.add_node("code", code_node)
graph.add_node("search", search_node)

graph.set_entry_point("supervisor")

graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_node"],
    {
        "summarizer": "summarizer",
        "research": "research",
        "code": "code",
        "search": "search",
    }
)

for node in ["summarizer", "research", "code", "search"]:
    graph.add_edge(node, END)

app = graph.compile()

# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    state: AgentState = {
        "messages": [SystemMessage(content="You are a helpful AI assistant.")]
    }

    print("Agent ready. Type 'exit' to quit.")

    while True:
        user = input("\nYou: ")
        if user.lower() in {"exit", "quit"}:
            break

        state["messages"].append(HumanMessage(content=user))
        state = app.invoke(state)

        print(state["messages"][-1].content)

