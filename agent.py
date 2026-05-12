# import os
# import uuid
# from typing import TypedDict, List, Dict
# from dotenv import load_dotenv

# from langsmith import traceable
# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph
# from langgraph.checkpoint.memory import MemorySaver

# from src.tools.vfs import VFS
# from src.subagents.web_search_agent import web_agent_app
# from src.subagents.summarizer_agent import summarizer_app
# from src.tools.writetodos import write_todos

# # ======================================================
# # ENV SETUP
# # ======================================================
# load_dotenv()

# if not os.getenv("GROQ_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
#     raise RuntimeError("Missing API keys")

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "cognibot"

# # ======================================================
# # LLM
# # ======================================================
# llm = ChatGroq(
#     api_key=os.getenv("GROQ_API_KEY"),
#     model="llama-3.1-8b-instant",
#     temperature=0,
# )

# @traceable(name="groq_llm_call", run_type="llm")
# def call_llm(messages):
#     return llm.invoke(messages).content

# # ======================================================
# # STATE
# # ======================================================
# class State(TypedDict):
#     input: str
#     messages: List[Dict[str, str]]
#     vfs: Dict[str, str]
#     delegated_result: str

# # ======================================================
# # WRITE TODOS (INJECT LLM)
# # ======================================================
# @traceable(name="write_todos_wrapper", run_type="chain")
# def write_todos_node(state: State) -> State:
#     return write_todos(state, call_llm)

# # ======================================================
# # DELEGATE TASK
# # ======================================================
# @traceable(name="delegate_task_tool", run_type="chain")
# def delegate_task(state: State) -> State:
#     web_state = {
#         "query": state["input"],
#         "result": ""
#     }

#     web_state = web_agent_app.invoke(
#         web_state,
#         config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
#     )

#     if web_state.get("result"):
#         summary_state = {
#             "text": web_state["result"],
#             "summary": ""
#         }

#         summary_state = summarizer_app.invoke(
#             summary_state,
#             config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
#         )

#         state["delegated_result"] = summary_state["summary"]
#     else:
#         state["delegated_result"] = ""

#     vfs = VFS.from_dict(state["vfs"])
#     vfs.write_file("research.txt", state["delegated_result"])
#     state["vfs"] = vfs.to_dict()

#     return state

# # ======================================================
# # FINAL RESPONSE
# # ======================================================
# @traceable(
#     name="assistant_response_tool",
#     run_type="chain",
# )
# def assistant_response(state: State) -> State:
    
#     trace_input = state["input"]

#     vfs = VFS.from_dict(state["vfs"])
#     research = vfs.read_file("research.txt", traced=True)

#     prompt = f"""
# User Question:
# {trace_input}

# Research Notes:
# {research}

# Produce a clear, well-structured final answer.
# """

#     reply = call_llm([
#         {"role": "system", "content": "You are an autonomous research agent."},
#         {"role": "user", "content": prompt}
#     ])

#     state["messages"].append({"role": "assistant", "content": reply})

#     state["input"] = ""

#     return state

# # ======================================================
# # GRAPH
# # ======================================================
# graph = StateGraph(State)

# graph.add_node("write_todos", write_todos_node)
# graph.add_node("delegate_task", delegate_task)
# graph.add_node("assistant", assistant_response)

# graph.add_edge("__start__", "write_todos")
# graph.add_edge("write_todos", "delegate_task")
# graph.add_edge("delegate_task", "assistant")
# graph.add_edge("assistant", "__end__")

# app = graph.compile(checkpointer=MemorySaver())
# import os
# import uuid
# from typing import TypedDict, List, Dict
# from dotenv import load_dotenv

# from langsmith import traceable
# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph
# from langgraph.checkpoint.memory import MemorySaver

# from src.tools.vfs import VFS
# from src.subagents.web_search_agent import web_agent_app
# from src.subagents.summarizer_agent import summarizer_app
# from src.tools.writetodos import write_todos

# # ======================================================
# # ENV SETUP
# # ======================================================
# load_dotenv()

# if not os.getenv("GROQ_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
#     raise RuntimeError("Missing API keys")

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "cognibot"

# # ======================================================
# # LLM
# # ======================================================
# llm = ChatGroq(
#     api_key=os.getenv("GROQ_API_KEY"),
#     model="llama-3.1-8b-instant",
#     temperature=0,
# )

# @traceable(name="groq_llm_call", run_type="llm")
# def call_llm(messages):
#     return llm.invoke(messages).content

# # ======================================================
# # STATE
# # ======================================================
# class State(TypedDict):
#     input: str
#     messages: List[Dict[str, str]]
#     vfs: Dict[str, str]
#     delegated_result: str

# # ======================================================
# # WRITE TODOS (UNCHANGED)
# # ======================================================
# @traceable(name="write_todos_wrapper", run_type="chain")
# def write_todos_node(state: State) -> State:
#     return write_todos(state, call_llm)

# # ======================================================
# # 🔥 DYNAMIC DELEGATION DECISION (NEW)
# # ======================================================
# @traceable(name="decide_delegation", run_type="llm")
# def decide_delegation(task: str) -> str:
#     prompt = f"""
# You are an autonomous agent.

# Given the task:
# "{task}"

# Decide the best action.
# Reply with ONLY ONE word:
# - web_search
# - summarize
# - llm
# """
#     return call_llm([{"role": "user", "content": prompt}]).strip().lower()

# # ======================================================
# # DELEGATE TASK (UPDATED, NOT RESTRUCTURED)
# # ======================================================
# @traceable(name="delegate_task_tool", run_type="chain")
# def delegate_task(state: State) -> State:
#     task = state["input"]

#     decision = decide_delegation(task)

#     result = ""

#     # ---------------- WEB SEARCH ----------------
#     if decision == "web_search":
#         web_state = {
#             "query": task,
#             "result": ""
#         }

#         web_state = web_agent_app.invoke(
#             web_state,
#             config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
#         )

#         result = web_state.get("result", "")

#     # ---------------- SUMMARIZATION ----------------
#     elif decision == "summarize":
#         summary_state = {
#             "text": state["delegated_result"],
#             "summary": ""
#         }

#         summary_state = summarizer_app.invoke(
#             summary_state,
#             config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
#         )

#         result = summary_state.get("summary", "")

#     # ---------------- DIRECT LLM ----------------
#     else:
#         result = call_llm([
#             {"role": "user", "content": task}
#         ])

#     # ---------------- STORE RESULT ----------------
#     state["delegated_result"] = result

#     vfs = VFS.from_dict(state["vfs"])
#     vfs.write_file("research.txt", result)
#     state["vfs"] = vfs.to_dict()

#     return state

# # ======================================================
# # FINAL RESPONSE (ENSURES LINKS ARE PRESERVED)
# # ======================================================
# @traceable(name="assistant_response_tool", run_type="chain")
# def assistant_response(state: State) -> State:

#     trace_input = state["input"]

#     vfs = VFS.from_dict(state["vfs"])
#     research = vfs.read_file("research.txt", traced=True)

#     prompt = f"""
# User Question:
# {trace_input}

# Research Notes (with sources, if available):
# {research}

# Instructions:
# - Preserve all URLs
# - Cite sources clearly if present
# - Produce a clear, well-structured answer
# """

#     reply = call_llm([
#         {"role": "system", "content": "You are an autonomous research agent. Always include source links if provided."},
#         {"role": "user", "content": prompt}
#     ])

#     state["messages"].append({"role": "assistant", "content": reply})
#     state["input"] = ""

#     return state

# # ======================================================
# # GRAPH (UNCHANGED)
# # ======================================================
# graph = StateGraph(State)

# graph.add_node("write_todos", write_todos_node)
# graph.add_node("delegate_task", delegate_task)
# graph.add_node("assistant", assistant_response)

# graph.add_edge("__start__", "write_todos")
# graph.add_edge("write_todos", "delegate_task")
# graph.add_edge("delegate_task", "assistant")
# graph.add_edge("assistant", "__end__")

# app = graph.compile(checkpointer=MemorySaver())
# import os
# import uuid
# from typing import TypedDict, List, Dict
# from dotenv import load_dotenv

# from langsmith import traceable
# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph
# from langgraph.checkpoint.memory import MemorySaver

# from src.tools.vfs import VFS
# from src.subagents.web_search_agent import web_agent_app
# from src.subagents.summarizer_agent import summarizer_app
# from src.tools.writetodos import write_todos

# # ======================================================
# # ENV SETUP
# # ======================================================
# load_dotenv()

# if not os.getenv("GROQ_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
#     raise RuntimeError("Missing API keys")

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "cognibot"

# # ======================================================
# # LLM
# # ======================================================
# llm = ChatGroq(
#     api_key=os.getenv("GROQ_API_KEY"),
#     model="llama-3.1-8b-instant",
#     temperature=0,
# )

# @traceable(name="groq_llm_call", run_type="llm")
# def call_llm(messages):
#     return llm.invoke(messages).content.strip()

# # ======================================================
# # STATE
# # ======================================================
# class State(TypedDict):
#     input: str
#     messages: List[Dict[str, str]]
#     vfs: Dict[str, str]
#     delegated_result: str

# # ======================================================
# # WRITE TODOS (UNCHANGED)
# # ======================================================
# @traceable(name="write_todos_wrapper", run_type="chain")
# def write_todos_node(state: State) -> State:
#     return write_todos(state, call_llm)

# # ======================================================
# # 🔥 LLM-BASED INTENT ROUTER (CORE FIX)
# # ======================================================
# @traceable(name="decide_delegation", run_type="llm")
# def decide_delegation(task: str) -> str:
#     prompt = f"""
# You are an intent router for a multi-agent system.

# Decide which execution path is required.

# Choose exactly ONE:
# - web_only → needs fresh or factual information from the internet
# - summarize_only → user provides content and wants it condensed
# - web_then_summarize → needs web research followed by summarization

# Return ONLY the option string.

# Task:
# {task}
# """
#     return call_llm([
#         {"role": "system", "content": "You are a strict intent classifier."},
#         {"role": "user", "content": prompt}
#     ])

# # ======================================================
# # DELEGATE TASK (FULLY DYNAMIC)
# # ======================================================
# @traceable(name="delegate_task_tool", run_type="chain")
# def delegate_task(state: State) -> State:
#     task = state["input"]
#     decision = decide_delegation(task)

#     result = ""

#     # -------- SUMMARIZE ONLY --------
#     if decision == "summarize_only":
#         summary_state = {
#             "text": task,
#             "summary": ""
#         }
#         summary_state = summarizer_app.invoke(
#             summary_state,
#             config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
#         )
#         result = summary_state["summary"]

#     # -------- WEB ONLY --------
#     elif decision == "web_only":
#         web_state = {
#             "query": task,
#             "result": ""
#         }
#         web_state = web_agent_app.invoke(
#             web_state,
#             config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
#         )
#         result = web_state["result"]

#     # -------- WEB → SUMMARIZE (⭐ IMPORTANT CASE) --------
#     elif decision == "web_then_summarize":
#         web_state = {
#             "query": task,
#             "result": ""
#         }
#         web_state = web_agent_app.invoke(
#             web_state,
#             config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
#         )

#         summary_state = {
#             "text": web_state["result"],
#             "summary": ""
#         }
#         summary_state = summarizer_app.invoke(
#             summary_state,
#             config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
#         )

#         result = summary_state["summary"]

#     else:
#         raise ValueError(f"Unknown delegation decision: {decision}")

#     # -------- STORE RESULT --------
#     state["delegated_result"] = result

#     vfs = VFS.from_dict(state["vfs"])
#     vfs.write_file("research.txt", result)
#     state["vfs"] = vfs.to_dict()

#     return state

# # ======================================================
# # FINAL RESPONSE (LINK-SAFE)
# # ======================================================
# @traceable(name="assistant_response_tool", run_type="chain")
# def assistant_response(state: State) -> State:
#     vfs = VFS.from_dict(state["vfs"])
#     research = vfs.read_file("research.txt", traced=True)

#     prompt = f"""
# User Question:
# {state["input"]}

# Research Notes:
# {research}

# Rules:
# - Preserve all URLs exactly
# - Do not hallucinate sources
# - Produce a clear, structured answer
# """

#     reply = call_llm([
#         {"role": "system", "content": "You are an autonomous research agent."},
#         {"role": "user", "content": prompt}
#     ])

#     state["messages"].append({"role": "assistant", "content": reply})
#     state["input"] = ""

#     return state

# # ======================================================
# # GRAPH
# # ======================================================
# graph = StateGraph(State)

# graph.add_node("write_todos", write_todos_node)
# graph.add_node("delegate_task", delegate_task)
# graph.add_node("assistant", assistant_response)

# graph.add_edge("__start__", "write_todos")
# graph.add_edge("write_todos", "delegate_task")
# graph.add_edge("delegate_task", "assistant")
# graph.add_edge("assistant", "__end__")

# app = graph.compile(checkpointer=MemorySaver())
import os
import uuid
from typing import TypedDict, List, Dict
from dotenv import load_dotenv

from langsmith import traceable
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.tools.vfs import VFS
from src.subagents.web_search_agent import web_agent_app
from src.subagents.summarizer_agent import summarizer_app
from src.tools.writetodos import write_todos

# ======================================================
# ENV SETUP
# ======================================================
load_dotenv()

if not os.getenv("GROQ_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
    raise RuntimeError("Missing API keys")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "cognibot"

# ======================================================
# LLM
# ======================================================
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0,
)

@traceable(name="groq_llm_call", run_type="llm")
def call_llm(messages):
    return llm.invoke(messages).content.strip()

# ======================================================
# STATE
# ======================================================
class State(TypedDict):
    input: str
    messages: List[Dict[str, str]]
    vfs: Dict[str, str]
    delegated_result: str

# ======================================================
# WRITE TODOS
# ======================================================
@traceable(name="write_todos_wrapper", run_type="chain")
def write_todos_node(state: State) -> State:
    return write_todos(state, call_llm)

# ======================================================
# 🔥 LLM INTENT ROUTER (STRICT + SAFE)
# ======================================================
@traceable(name="decide_delegation", run_type="llm")
def decide_delegation(task: str) -> str:
    prompt = f"""
You are an intent router for a multi-agent AI system.

You MUST output ONLY ONE TOKEN.
No explanations.
No punctuation.
No quotes.

Allowed outputs:
summarize_only
web_only
web_then_summarize

Decision rules:
- summarize_only → conceptual/common knowledge explanation
- web_only → needs factual or external information
- web_then_summarize → research + condensation required

Task:
{task}

Output:
"""
    response = call_llm([
        {"role": "system", "content": "You are a strict classifier."},
        {"role": "user", "content": prompt}
    ])

    return response.strip().lower()

# ======================================================
# DELEGATION EXECUTION (DYNAMIC + TRACEABLE)
# ======================================================
@traceable(name="delegate_task_tool", run_type="chain")
def delegate_task(state: State) -> State:
    task = state["input"]
    raw_decision = decide_delegation(task)

    # -------- SAFETY NORMALIZATION --------
    if "web_then_summarize" in raw_decision:
        decision = "web_then_summarize"
    elif "web_only" in raw_decision:
        decision = "web_only"
    elif "summarize_only" in raw_decision:
        decision = "summarize_only"
    else:
        raise ValueError(f"Invalid delegation output: {raw_decision}")

    result = ""

    # -------- SUMMARIZE ONLY --------
    if decision == "summarize_only":
        summary_state = {
            "text": task,
            "summary": ""
        }
        summary_state = summarizer_app.invoke(
            summary_state,
            config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
        )
        result = summary_state["summary"]

    # -------- WEB ONLY --------
    elif decision == "web_only":
        web_state = {
            "query": task,
            "result": ""
        }
        web_state = web_agent_app.invoke(
            web_state,
            config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
        )
        result = web_state["result"]

    # -------- WEB → SUMMARIZE --------
    elif decision == "web_then_summarize":
        web_state = {
            "query": task,
            "result": ""
        }
        web_state = web_agent_app.invoke(
            web_state,
            config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
        )

        summary_state = {
            "text": web_state["result"],
            "summary": ""
        }
        summary_state = summarizer_app.invoke(
            summary_state,
            config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
        )

        result = summary_state["summary"]

    # -------- STORE RESULT --------
    state["delegated_result"] = result

    vfs = VFS.from_dict(state["vfs"])
    vfs.write_file("research.txt", result)
    state["vfs"] = vfs.to_dict()

    return state

# ======================================================
# FINAL RESPONSE NODE (LINK SAFE)
# ======================================================
@traceable(name="assistant_response_tool", run_type="chain")
def assistant_response(state: State) -> State:
    vfs = VFS.from_dict(state["vfs"])
    research = vfs.read_file("research.txt", traced=True)

    prompt = f"""
User Question:
{state["input"]}

Research Notes:
{research}

Rules:
- Preserve URLs exactly
- Do NOT hallucinate sources
- Provide a clear structured answer
"""

    reply = call_llm([
        {"role": "system", "content": "You are an autonomous research agent."},
        {"role": "user", "content": prompt}
    ])

    state["messages"].append({"role": "assistant", "content": reply})
    state["input"] = ""

    return state

# ======================================================
# GRAPH
# ======================================================
graph = StateGraph(State)

graph.add_node("write_todos", write_todos_node)
graph.add_node("delegate_task", delegate_task)
graph.add_node("assistant", assistant_response)

graph.add_edge("__start__", "write_todos")
graph.add_edge("write_todos", "delegate_task")
graph.add_edge("delegate_task", "assistant")
graph.add_edge("assistant", "__end__")

app = graph.compile(checkpointer=MemorySaver())
