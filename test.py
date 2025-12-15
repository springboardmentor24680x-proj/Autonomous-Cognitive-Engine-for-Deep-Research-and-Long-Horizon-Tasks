# test.py
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from source.vfs import VFS

import groq

# ==============================
# LOAD ENV VARIABLES
# ==============================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY or not LANGSMITH_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Missing API keys")

client = groq.Client(api_key=GROQ_API_KEY)

os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Cognibot-Autonomous-Agent"

# ==============================
# STATE
# ==============================
class State(TypedDict):
    input: str
    messages: List[Dict[str, Any]]
    vfs: Dict[str, str]
    recent_files_changes: Dict[str, List[str]]
    trace_id: str
    route: str

# ==============================
# GROQ CALL WITH MEMORY
# ==============================
def call_groq_with_memory(state: State, prompt_override: str = None) -> str:
    messages = []
    for msg in state["messages"]:
        messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({
        "role": "user",
        "content": prompt_override if prompt_override else state["input"]
    })
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1500
    )
    return resp.choices[0].message.content

# ==============================
# VFS HELPERS
# ==============================
def write_file(state: State, filename: str, content: str):
    vfs = VFS.from_dict(state["vfs"])
    if filename in vfs.files:
        vfs.edit_file(filename, content)
        state["recent_files_changes"]["edited"].append(filename)
    else:
        vfs.write_file(filename, content)
        state["recent_files_changes"]["created"].append(filename)
    state["vfs"] = vfs.to_dict()

def read_file(state: State, filename: str):
    return VFS.from_dict(state["vfs"]).read_file(filename)

def ls_files(state: State):
    return VFS.from_dict(state["vfs"]).ls()

# ==============================
# TOOLS
# ==============================
def write_todos_tool(state: State):
    prompt = f"Break the following request into numbered TODO steps.\nRequest:\n{state['input']}"
    todos = call_groq_with_memory(state, prompt)
    write_file(state, "intermediary_todos.txt", todos)
    state["messages"].append({"role": "assistant", "text": todos})
    return state

def plan_todo_tool(state: State):
    prev = read_file(state, "intermediary_todos.txt")
    prompt = f"Create a phase-based plan from these TODOs:\n{prev}"
    plan = call_groq_with_memory(state, prompt)
    write_file(state, "full_output.txt", plan)
    state["messages"].append({"role": "assistant", "text": plan})
    return state

# ==============================
# MILESTONE 3 – INTENT ROUTER
# ==============================
def classify_intent(user_input: str) -> str:
    text = user_input.lower()
    # Action-based tasks (internal LLM)
    if any(word in text for word in ["invite", "schedule", "todo", "remind", "draft", "plan"]):
        return "action"
    # Research-based tasks
    if any(word in text for word in ["research", "find", "analyze", "study"]):
        return "research"
    return "general"

def decide_delegation_tool(state: State):
    intent = classify_intent(state["input"])

    if intent == "action":
        state["route"] = "internal"
    elif intent == "research":
        # fallback to existing rules
        prompt = f"Decide task handling.\nTask:\n{state['input']}\nRules:\n- Needs internet/latest info → WEB\n- Needs summary → SUMMARY\n- Else → INTERNAL\nReturn only one word."
        decision = call_groq_with_memory(state, prompt).upper()
        if "WEB" in decision:
            state["route"] = "web"
        elif "SUMMARY" in decision:
            state["route"] = "summary"
        else:
            state["route"] = "internal"
    else:
        state["route"] = "internal"
    return state

# ==============================
# WEB SEARCH SUB-AGENT
# ==============================
from tavily import TavilyClient
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def web_search_tool(state: State):
    result = tavily.search(state["input"], max_results=5)
    formatted = ""
    for r in result["results"]:
        formatted += f"- {r['title']}\n{r['content']}\nSource: {r['url']}\n\n"
    write_file(state, "web_results.txt", formatted)
    state["messages"].append({"role": "assistant", "text": formatted})
    return state

# ==============================
# SUMMARY SUB-AGENT
# ==============================
def summarize_tool(state: State):
    text = read_file(state, "web_results.txt")
    prompt = f"Summarize the following information:\n{text}"
    summary = call_groq_with_memory(state, prompt)
    write_file(state, "summary.txt", summary)
    state["messages"].append({"role": "assistant", "text": summary})
    return state

# ==============================
# INTERNAL LLM TOOL
# ==============================
def internal_llm_tool(state: State):
    response = call_groq_with_memory(state)
    write_file(state, "internal_response.txt", response)
    state["messages"].append({"role": "assistant", "text": response})
    return state

# ==============================
# LANGGRAPH SETUP
# ==============================
graph = StateGraph(State)

graph.add_node("todos", write_todos_tool)
graph.add_node("plan", plan_todo_tool)
graph.add_node("decide", decide_delegation_tool)
graph.add_node("web", web_search_tool)
graph.add_node("summary", summarize_tool)
graph.add_node("internal", internal_llm_tool)

graph.add_edge("__start__", "todos")
graph.add_edge("todos", "plan")
graph.add_edge("plan", "decide")

graph.add_conditional_edges(
    "decide",
    lambda s: s["route"],
    {
        "web": "web",
        "summary": "summary",
        "internal": "internal",
    }
)

graph.add_edge("web", "__end__")
graph.add_edge("summary", "__end__")
graph.add_edge("internal", "__end__")

app = graph.compile(checkpointer=MemorySaver())

# ==============================
# RUNNER
# ==============================
def run_agent(state: State, user_input: str):
    state["input"] = user_input
    state["messages"].append({"role": "user", "text": user_input})
    updated = app.invoke(
        state,
        config={"configurable": {"thread_id": state["trace_id"]}}
    )
    return updated

# ==============================
# CLI
# ==============================
if __name__ == "__main__":
    print("=== Autonomous Cognitive Agent (Milestone 3) ===")
    state: State = {
        "input": "",
        "messages": [],
        "vfs": {},
        "recent_files_changes": {"created": [], "edited": []},
        "trace_id": f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "route": "",
    }

    while True:
        cmd = input("\nEnter request: ").strip()
        if cmd.lower() == "exit":
            break
        if cmd.startswith("show "):
            fname = cmd.split(" ", 1)[1]
            print(read_file(state, fname))
            continue
        state = run_agent(state, cmd)
        print("\n--- Assistant Output ---")
        for msg in reversed(state["messages"]):
            if msg["role"] == "assistant":
                print(msg["text"])
                break
        print("\nFiles in VFS:")
        for f in ls_files(state):
            print("-", f)
