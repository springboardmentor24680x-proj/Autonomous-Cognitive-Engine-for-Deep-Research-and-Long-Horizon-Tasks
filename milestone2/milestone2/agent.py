# agent.py
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

# VFS tools (Milestone 2 – context offloading)
from tools.vfs_tools import ls, read_file, write_file, edit_file

# -----------------------------
# ENV SETUP
# -----------------------------
load_dotenv()

# -----------------------------
# LLM (LangSmith enabled)
# -----------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4
)

# LangSmith tracing config
TRACE_CONFIG = RunnableConfig(tags=["milestone-3", "sub-agent-delegation"])

# -----------------------------
# PLANNER SUB-AGENT
# -----------------------------
def planner_agent(user_query):
    """
    Breaks a complex query into clear actionable steps.
    """
    messages = [
        SystemMessage(
            content="Break the user request into clear, concise actionable steps."
        ),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages, config=TRACE_CONFIG)

    steps = [
        step.strip("-• ")
        for step in response.content.split("\n")
        if step.strip()
    ]

    return steps[:5]  # limit number of steps

# -----------------------------
# WORKER SUB-AGENT
# -----------------------------
def worker_agent(step):
    """
    Solves a single step delegated by the planner.
    """
    messages = [
        SystemMessage(
            content="You are a specialized sub-agent. Solve only the given step clearly."
        ),
        HumanMessage(content=step)
    ]

    response = llm.invoke(messages, config=TRACE_CONFIG)
    return response.content

# -----------------------------
# SUPERVISOR AGENT
# -----------------------------
def supervisor_node(state):
    user_query = state["user_query"]

    # Maintain conversation memory
    state.setdefault("chat_history", []).append({
        "role": "user",
        "content": user_query
    })

    # Decide complexity (simple heuristic)
    is_complex = len(user_query.split()) > 6

    # -------------------------
    # COMPLEX QUERY → DELEGATE
    # -------------------------
    if is_complex:
        steps = planner_agent(user_query)

        results = []
        for step in steps:
            output = worker_agent(step)
            results.append(f"### {step}\n{output}")

        final_answer = "\n\n".join(results)

    # -------------------------
    # SIMPLE QUERY → DIRECT
    # -------------------------
    else:
        response = llm.invoke(
            [HumanMessage(content=user_query)],
            config=TRACE_CONFIG
        )
        final_answer = response.content

    # Save result
    state["final_answer"] = final_answer
    state["chat_history"].append({
        "role": "assistant",
        "content": final_answer
    })

    return state

# -----------------------------
# LANGGRAPH BUILD
# -----------------------------
workflow = StateGraph(dict)
workflow.add_node("supervisor", supervisor_node)
workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", END)

graph = workflow.compile()