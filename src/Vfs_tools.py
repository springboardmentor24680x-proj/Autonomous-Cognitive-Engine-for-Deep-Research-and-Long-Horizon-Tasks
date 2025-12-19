from typing import TypedDict, Annotated
import operator
import os
import json
import uuid

from langchain.tools import tool
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

# -------------------------------
# Environment
# -------------------------------
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "vfs-agent"

# -------------------------------
# Persistent VFS
# -------------------------------
VFS_FILE = "vfs.json"


def load_vfs():
    if os.path.exists(VFS_FILE):
        with open(VFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_vfs(vfs):
    with open(VFS_FILE, "w", encoding="utf-8") as f:
        json.dump(vfs, f, indent=2)


# -------------------------------
# LLM
# -------------------------------
model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4,
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    max_tokens=700,
)

# -------------------------------
# VFS TOOLS
# -------------------------------
@tool
def ls(vfs: dict) -> list:
    """List all files"""
    return list(vfs.keys())


@tool
def read_file(filename: str, vfs: dict) -> str:
    """Read a file"""
    return vfs.get(filename, f"File '{filename}' not found.")


@tool
def write_file(filename: str, content: str, vfs: dict) -> str:
    """Write a file"""
    vfs[filename] = content
    save_vfs(vfs)
    return "saved"


@tool
def edit_file(filename: str, new_content: str, vfs: dict) -> str:
    """Edit a file"""
    if filename not in vfs:
        return "file not found"
    vfs[filename] = new_content
    save_vfs(vfs)
    return "updated"


@tool
def show_current_info(vfs: dict) -> str:
    """Show all stored info"""
    return "\n".join(vfs.keys()) if vfs else "No data stored."


TOOLS = [ls, read_file, write_file, edit_file, show_current_info]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

model_with_tools = model.bind_tools(TOOLS)

# -------------------------------
# STATE
# -------------------------------
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    vfs: dict


# -------------------------------
# SYSTEM PROMPT
# -------------------------------
SYSTEM_PROMPT = """
You are a friendly chat assistant.

You can use tools silently to save or read information.
Never mention tools or files unless the user asks.
Never show function calls.
Just chat naturally like a human.
"""


# -------------------------------
# LLM NODE
# -------------------------------
def llm_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

    response = model_with_tools.invoke(messages)

    return {
        "messages": state["messages"] + [response],
        "vfs": state["vfs"],
    }


# -------------------------------
# TOOL NODE
# -------------------------------
def tool_node(state: AgentState):
    last = state["messages"][-1]
    tool_messages = []

    for call in last.tool_calls:
        tool = TOOLS_BY_NAME.get(call["name"])
        if not tool:
            continue

        args = call["args"]
        args["vfs"] = state["vfs"]

        result = tool.invoke(args)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
            )
        )

    return {
        "messages": state["messages"] + tool_messages,
        "vfs": state["vfs"],
    }


# -------------------------------
# ROUTING
# -------------------------------
def route(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tool"
    return END


# -------------------------------
# GRAPH
# -------------------------------
graph = StateGraph(AgentState)

graph.add_node("llm", llm_node)
graph.add_node("tool", tool_node)

graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", route, ["tool", END])
graph.add_edge("tool", "llm")

agent = graph.compile()


# -------------------------------
# RUNNER
# -------------------------------
def run_agent(user_input: str, state=None):
    if state is None:
        state = {
            "messages": [HumanMessage(content=user_input)],
            "vfs": load_vfs(),
        }
    else:
        state["messages"].append(HumanMessage(content=user_input))

    return agent.invoke(state)


# -------------------------------
# CLI
# -------------------------------
if __name__ == "__main__":
    print("VFS Chat Agent. Type 'exit' to quit.\n")

    state = None

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() == "exit":
            break

        state = run_agent(user_text, state)

        #  PRINT ONLY CLEAN AI CHAT (NO TOOLS)
        last_msg = state["messages"][-1]

        if isinstance(last_msg, AIMessage) and last_msg.content and not last_msg.tool_calls:
            print("AI:", last_msg.content.strip(),"\n")
