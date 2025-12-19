import os
import json
from dotenv import load_dotenv
from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
import groq

from src.vfs import VFS
from src.subagents.web_search_agent import web_agent_app
from src.subagents.summarizer_agent import summarizer_app

# ======================================================
# ENV SETUP
# ======================================================
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not GROQ_API_KEY or not LANGSMITH_API_KEY:
    raise ValueError("Missing API keys")

client = groq.Client(api_key=GROQ_API_KEY)

# ======================================================
# STATE
# ======================================================
class State(TypedDict):
    input: str
    messages: List[Dict[str, str]]
    vfs: Dict[str, str]
    delegated_result: str

# ======================================================
# LLM CALL
# ======================================================
@traceable(name="groq_llm_call", run_type="llm")
def call_llm(messages: List[Dict[str, str]]) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1200
    )
    return resp.choices[0].message.content.strip()

# ======================================================
# TODO MANAGER (INTERNAL ONLY)
# ======================================================
@traceable(name="write_todos_tool", run_type="chain")
def write_todos(state: State) -> State:
    vfs = VFS.from_dict(state["vfs"])
    existing = vfs.read_file("intermediary_todos.txt", traced=True)

    prompt = f"""
Maintain an INTERNAL TODO list.

Existing TODOs:
{existing if existing else "(none)"}

New instruction:
{state["input"]}

Rules:
- Never delete existing tasks unless explicitly requested
- Add new tasks if required
- Bullet points only
"""
    todos = call_llm([{"role": "user", "content": prompt}])
    vfs.write_file("intermediary_todos.txt", todos)
    state["vfs"] = vfs.to_dict()
    return state

# ======================================================
# DELEGATION 
# ======================================================
@traceable(name="delegate_task_tool", run_type="chain")
def delegate(state: State) -> State:
    """
    ALWAYS performs web search first to guarantee up-to-date answers.
    LLM is used only to summarize web results.
    """

    delegated_text = ""

    # 🔹 Always use Tavily for real-world queries
    web_state = {
        "query": state["input"],
        "result": ""
    }

    web_state = web_agent_app.invoke(
        web_state,
        config={"configurable": {"thread_id": "web_search"}}
    )

    delegated_text = web_state.get("result", "")

    # 🔹 Summarize web results if available
    if delegated_text and delegated_text != "[No results found]":
        summary_state = {
            "text": delegated_text,
            "summary": ""
        }

        summary_state = summarizer_app.invoke(
            summary_state,
            config={"configurable": {"thread_id": "summarizer"}}
        )

        state["delegated_result"] = summary_state.get("summary", "")
    else:
        state["delegated_result"] = ""

    return state

# ======================================================
# ASSISTANT RESPONSE 
# ======================================================
@traceable(name="assistant_response_tool", run_type="chain")
def assistant_response(state: State) -> State:
    messages = state["messages"] + [
        {"role": "system", "content": "You are Agent. Respond clearly and naturally."},
        {
            "role": "user",
            "content": f"""
User input:
{state["input"]}

Delegated result (if any):
{state["delegated_result"]}
"""
        }
    ]

    reply = call_llm(messages)
    state["messages"].append({"role": "assistant", "content": reply})
    return state

# ======================================================
# GRAPH
# ======================================================
graph = StateGraph(State)
graph.add_node("write_todos", write_todos)
graph.add_node("delegate_task", delegate)
graph.add_node("assistant", assistant_response)

graph.add_edge("__start__", "write_todos")
graph.add_edge("write_todos", "delegate_task")
graph.add_edge("delegate_task", "assistant")
graph.add_edge("assistant", "__end__")

app = graph.compile(checkpointer=MemorySaver())

# ======================================================
# TURN FUNCTION 
# ======================================================
@traceable(name="LangGraph", run_type="chain")
def run_turn(state: State, user_input: str) -> State:
    state["input"] = user_input
    state["messages"].append({"role": "user", "content": user_input})

    new_state = app.invoke(
        state,
        config={"configurable": {"thread_id": "cognibot"}}
    )

    return new_state

# ======================================================
# CLI
# ======================================================
def main():
    print("=== Autonomous Cognitive Agent ===")
    print("Type 'exit' to quit\n")

    state: State = {
        "input": "",
        "messages": [],
        "vfs": {},
        "delegated_result": ""
    }

    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() == "exit":
            break

        state = run_turn(state, user)
        print("\nAssistant:", state["messages"][-1]["content"], "\n")
if __name__ == "__main__":
    main()