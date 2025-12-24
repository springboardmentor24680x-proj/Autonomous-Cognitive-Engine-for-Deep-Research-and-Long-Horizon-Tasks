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
    return llm.invoke(messages).content

# ======================================================
# STATE
# ======================================================
class State(TypedDict):
    input: str
    messages: List[Dict[str, str]]
    vfs: Dict[str, str]
    delegated_result: str

# ======================================================
# WRITE TODOS (INJECT LLM)
# ======================================================
@traceable(name="write_todos_wrapper", run_type="chain")
def write_todos_node(state: State) -> State:
    return write_todos(state, call_llm)

# ======================================================
# DELEGATE TASK
# ======================================================
@traceable(name="delegate_task_tool", run_type="chain")
def delegate_task(state: State) -> State:
    web_state = {
        "query": state["input"],
        "result": ""
    }

    web_state = web_agent_app.invoke(
        web_state,
        config={"configurable": {"thread_id": f"web_{uuid.uuid4()}"}}
    )

    if web_state.get("result"):
        summary_state = {
            "text": web_state["result"],
            "summary": ""
        }

        summary_state = summarizer_app.invoke(
            summary_state,
            config={"configurable": {"thread_id": f"summary_{uuid.uuid4()}"}}
        )

        state["delegated_result"] = summary_state["summary"]
    else:
        state["delegated_result"] = ""

    vfs = VFS.from_dict(state["vfs"])
    vfs.write_file("research.txt", state["delegated_result"])
    state["vfs"] = vfs.to_dict()

    return state

# ======================================================
# FINAL RESPONSE
# ======================================================
@traceable(
    name="assistant_response_tool",
    run_type="chain",
)
def assistant_response(state: State) -> State:
    
    trace_input = state["input"]

    vfs = VFS.from_dict(state["vfs"])
    research = vfs.read_file("research.txt", traced=True)

    prompt = f"""
User Question:
{trace_input}

Research Notes:
{research}

Produce a clear, well-structured final answer.
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
