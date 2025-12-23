import os
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END
from langchain.tools import tool

# -----------------------------------------
# Load API Keys
# -----------------------------------------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

client = Groq(api_key=API_KEY)

# -----------------------------------------
# LLM Wrapper
# -----------------------------------------
def llm_call(messages):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content

# -----------------------------------------
# TOOL — TODO Planning Tool
# -----------------------------------------
@tool
def write_todos(request: str):
    """Break a user request into small, clear TODO steps."""
    system = "You are a task planner. Break the request into small, clear TODO steps."
    msg = [
        {"role": "system", "content": system},
        {"role": "user", "content": request}
    ]
    result = llm_call(msg)
    # Robust parsing: remove numbers, bullets, etc.
    todos = [{"task": t.strip().lstrip("0123456789.- ")} for t in result.split("\n") if t.strip()]
    return todos or []

# -----------------------------------------
# SUPERVISOR NODE0
# -----------------------------------------
def supervisor_node(state):
    if not state.get("todos"):
        todos = write_todos.invoke(state["user_query"])
        state["todos"] = todos or []
        state["current_step"] = 0
        if not state["todos"]:
            return state  # Nothing to do
    return state

# -----------------------------------------
# WORKER AGENT NODE
# -----------------------------------------
def worker_node(state):
    if state["current_step"] >= len(state.get("todos", [])):
        return state

    task = state["todos"][state["current_step"]]["task"]

    messages = [
        {"role": "system", "content": "You are a helpful worker agent. Execute the task."},
        {"role": "user", "content": task}
    ]

    result = llm_call(messages)
    state["todos"][state["current_step"]]["result"] = result or "No result returned"
    state["current_step"] += 1
    return state

# -----------------------------------------
# CHECK END CONDITION
# -----------------------------------------
def check_done(state):
    if state["current_step"] >= len(state.get("todos", [])):
        return END  #  Use constant
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
    {"worker": "worker", END: END}  #  Use constant
)

graph = workflow.compile()

# -----------------------------------------
# RUN
# -----------------------------------------
if __name__ == "__main__":
    print("Deep Cognitive Agent Ready!")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_query = input("You: ")
        if user_query.lower() in ("exit", "quit"):
            print("Exiting agent...")
            break

        state = {
            "user_query": user_query,
            "todos": [],
            "current_step": 0
        }

        # Increase recursion limit to avoid GraphRecursionError
        final_state = graph.invoke(state, config={"recursion_limit": 100})

        print("\n--- PLAN (TODO LIST) ---")
        for i, t in enumerate(final_state.get("todos", [])):
            print(f"{i+1}. {t['task']}")
            if "result" in t:
                print(f"   → {t['result']}")
        print("\n--- END ---\n")