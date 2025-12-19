from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)
from langchain_core.tools import tool

# Import your VFS
from vfs_tools import VirtualFileSystem

# ------------------------------------------
# ENV SETUP
# ------------------------------------------
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

if not os.getenv("LANGCHAIN_API_KEY"):
    raise Exception("Missing LANGCHAIN_API_KEY")

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise Exception("Missing OPENROUTER_API_KEY")

# ------------------------------------------
# STATE DEFINITION
# ------------------------------------------
class AgentState(TypedDict):
    messages: List[Any]
    todos: List[str]
    vfs: Dict[str, str]

# Initialize the VFS
vfs = VirtualFileSystem()

# ------------------------------------------
# SYSTEM PROMPT
# ------------------------------------------
SYSTEM_PROMPT = """
You are a helpful assistant.
Reply naturally like a normal chatbot.
"""

# ------------------------------------------
# TOOLS
# ------------------------------------------
@tool
def ls(tool_input: str = "") -> List[str]:
    """List all files in the virtual file system."""
    return vfs.ls()

@tool
def write_file(tool_input: str) -> str:
    """Write a file to the virtual file system."""
    args = json.loads(tool_input)
    filename = args["filename"]
    content = args["content"]
    vfs.write_file(filename, content)
    return f"File '{filename}' written successfully."

@tool
def read_file(tool_input: str) -> str:
    """Read a file from the virtual file system."""
    args = json.loads(tool_input)
    filename = args["filename"]
    content = vfs.read_file(filename)
    return content if content else f"File '{filename}' not found."

@tool
def edit_file(tool_input: str) -> str:
    """Edit an existing file in the virtual file system."""
    args = json.loads(tool_input)
    filename = args["filename"]
    content = args["content"]
    vfs.edit_file(filename, content)
    return f"File '{filename}' edited successfully."

@tool
def write_todos(tool_input: str) -> str:
    """Store a list of TODO items."""
    todos = json.loads(tool_input)
    return json.dumps(todos)

TOOLS = [
    write_todos,
    write_file,
    read_file,
    edit_file,
    ls
]

# ------------------------------------------
# LLM
# ------------------------------------------
llm = ChatOpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",
    model="gpt-4o-mini",
)
llm = llm.bind_tools(TOOLS)

# ------------------------------------------
# AGENT NODE
# ------------------------------------------
def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    response = llm.invoke(messages)
    messages.append(response)

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_map = {tool.name: tool for tool in TOOLS}
        for call in response.tool_calls:
            tool_fn = tool_map.get(call["name"])
            if tool_fn:
                tool_input = json.dumps(call["args"]) if call["args"] else ""
                result = tool_fn.run(tool_input)
                messages.append(
                    ToolMessage(
                        tool_call_id=call["id"],
                        content=str(result)
                    )
                )

    # ------------------------------
    # Save all chat messages to VFS as chat_history.json
    # ------------------------------
    chat_list = [
        {"role": "user", "content": m.content} if isinstance(m, HumanMessage)
        else {"role": "ai", "content": m.content}
        for m in messages if isinstance(m, (HumanMessage, AIMessage))
    ]
    vfs.write_file("chat_history.json", json.dumps(chat_list, indent=2))

    return state

# ------------------------------------------
# GRAPH
# ------------------------------------------
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)
app = graph.compile()

# ------------------------------------------
# MAIN LOOP
# ------------------------------------------
if __name__ == "__main__":
    state: AgentState = {
        "messages": [SystemMessage(content=SYSTEM_PROMPT)],
        "todos": [],
        "vfs": {}
    }

    print("Chatbot ready. Type 'exit' to quit.")

    while True:
        user = input("\nYou: ")
        if user.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        # ------------------------------
        # Handle VFS commands directly
        # ------------------------------
        parts = user.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "ls":
            files = vfs.ls()
            print("\n".join(files) if files else "No files in VFS.")
            continue
        elif cmd == "write_file":
            if args:
                try:
                    filename, content = args.split(maxsplit=1)
                    vfs.write_file(filename, content)
                    print(f"File '{filename}' written successfully.")
                except ValueError:
                    print("Usage: write_file <filename> <content>")
            else:
                print("Usage: write_file <filename> <content>")
            continue
        elif cmd == "read_file":
            if args:
                content = vfs.read_file(args)
                print(content if content else f"File '{args}' not found.")
            else:
                print("Usage: read_file <filename>")
            continue
        elif cmd == "edit_file":
            if args:
                try:
                    filename, content = args.split(maxsplit=1)
                    vfs.edit_file(filename, content)
                    print(f"File '{filename}' edited successfully.")
                except ValueError:
                    print("Usage: edit_file <filename> <content>")
            else:
                print("Usage: edit_file <filename> <content>")
            continue
        elif cmd == "write_todos":
            if args:
                todos = args.split(",")  # comma separated
                print(json.dumps(todos))
            else:
                print("Usage: write_todos todo1,todo2,...")
            continue

        # ------------------------------
        # Send normal text to AI
        # ------------------------------
        state["messages"].append(HumanMessage(content=user))
        state = app.invoke(state)

        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage):
            print(last_msg.content)
