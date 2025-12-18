# agent.py
import os
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END
from langchain.tools import tool
from langsmith import Client  # ← added
from datetime import datetime

# Import VFS tools
from tools.vfs_tools import ls, read_file, write_file, edit_file


# -----------------------------------------
# Load Environment Variables
# -----------------------------------------
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY missing in .env")

# -----------------------------------------
# LangSmith Tracing Setup (FULL)
# -----------------------------------------
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = "deep_agent_milestone2"

    smith = Client()
    print("✅ LangSmith tracing enabled")
else:
    print("⚠️ LangSmith key missing. Tracing disabled.")


# -----------------------------------------
# LLM WRAPPER
# -----------------------------------------
client = Groq(api_key=API_KEY)

def llm_call(messages):
    """Wrapper for Groq Chat Completion"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content


# -----------------------------------------
# TODO TOOL
# -----------------------------------------
@tool
def write_todos(request: str):
    """Break user query into TODO steps."""
    system = "You are a task planner. Break the user request into TODO steps, one per line."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": request}
    ]
    result = llm_call(messages)

    todos = [{"task": t.strip().lstrip('0123456789.- ')}
             for t in result.split("\n") if t.strip()]
    return todos or []


# -----------------------------------------
# SUPERVISOR NODE
# -----------------------------------------
def supervisor_node(state):
    if not state.get("todos"):
        state["todos"] = write_todos.invoke(state["user_query"])
        state["current_step"] = 0
    return state


# -----------------------------------------
# WORKER NODE
# -----------------------------------------
def worker_node(state):
    if state["current_step"] >= len(state["todos"]):
        return state

    task = state["todos"][state["current_step"]]["task"]

    system_prompt = """
You are a worker agent.
You may use tools: ls, read_file, write_file, edit_file.
If needed, store intermediate results in the VFS.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]

    result = llm_call(messages)

    state["todos"][state["current_step"]]["result"] = result
    state["current_step"] += 1
    return state


# -----------------------------------------
# END CHECK
# -----------------------------------------
def check_done(state):
    if state["current_step"] >= len(state["todos"]):
        return END
    return "worker"


# -----------------------------------------
# BUILD GRAPH
# -----------------------------------------
workflow = StateGraph(dict)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("worker", worker_node)

workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "worker")

workflow.add_conditional_edges(
    "worker",
    check_done,
    {"worker": "worker", END: END}
)

graph = workflow.compile()


# -----------------------------------------
# MAIN LOOP
# -----------------------------------------
if __name__ == "__main__":
    print("Milestone-2 Agent with LangSmith Tracing Ready!")
    print("Type 'exit' to stop.\n")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ["exit", "quit"]:
            print("Exiting agent...")
            break

        # Initial state
        state = {
            "user_query": user_query,
            "todos": [],
            "current_step": 0,
            "vfs": {}
        }

        final_state = graph.invoke(
            state,
            config={"recursion_limit": 100}
        )

        print("\n--- TODO PLAN ---")
        for i, t in enumerate(final_state["todos"]):
            print(f"{i+1}. {t['task']}")
            if "result" in t:
                print("   →", t["result"][:300])

        print("\n--- VFS FILES ---")
        for f in final_state["vfs"]:
            print("📄", f)

        print("\n--- END ---\n")