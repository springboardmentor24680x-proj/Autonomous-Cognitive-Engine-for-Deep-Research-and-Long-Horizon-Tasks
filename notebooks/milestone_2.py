import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AnyMessage,
)

from langgraph.graph import StateGraph, START, END


# --------------------------------------------------
# 1. ENV + LangSmith
# --------------------------------------------------
load_dotenv()

# LangSmith auto-tracing happens via ENV variables
# No extra code needed!


# --------------------------------------------------
# 2. Virtual File System (VFS)
# --------------------------------------------------
VFS_DIR = "vfs"
os.makedirs(VFS_DIR, exist_ok=True)


@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a virtual file."""
    path = os.path.join(VFS_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    return f"File '{filename}' written successfully."


@tool
def read_file(filename: str) -> str:
    """Read content from a virtual file."""
    path = os.path.join(VFS_DIR, filename)
    if not os.path.exists(path):
        return f"File '{filename}' not found."
    with open(path, "r") as f:
        return f.read()


@tool
def delete_file(filename: str) -> str:
    """Delete a virtual file."""
    path = os.path.join(VFS_DIR, filename)
    if not os.path.exists(path):
        return f"File '{filename}' not found."
    os.remove(path)
    return f"File '{filename}' deleted."


tools = [write_file, read_file, delete_file]
tools_by_name = {t.name: t for t in tools}


# --------------------------------------------------
# 3. LangGraph State
# --------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# --------------------------------------------------
# 4. LLM Setup
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=256
)

llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------
# 5. LLM Node
# --------------------------------------------------
MAX_MESSAGES = 4
def llm_node(state: AgentState):
    messages = state["messages"][-MAX_MESSAGES:]
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# --------------------------------------------------
# 6. Tool Node
# --------------------------------------------------
def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_messages}


# --------------------------------------------------
# 7. Router
# --------------------------------------------------
def router(state: AgentState):
    last = state["messages"][-1]

    # If last message is from TOOL → stop
    if isinstance(last, ToolMessage):
        return END

    # If LLM wants to call a tool → go to tool node
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool_node"

    # Otherwise stop
    return END



# --------------------------------------------------
# 8. Build Graph
# --------------------------------------------------
builder = StateGraph(AgentState)

builder.add_node("llm", llm_node)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", router)
builder.add_edge("tool_node", "llm")

agent = builder.compile()


# --------------------------------------------------
# 9. CLI Loop
# --------------------------------------------------
def main():
    print("\n LangSmith-Traced VFS Agent")
    print("Try: write notes.txt Hello")
    print("Try: read notes.txt")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        state = {
            "messages": [
                SystemMessage(content="Use file tools when needed."),
                HumanMessage(content=user_input),
            ]
        }

        result = agent.invoke(
    state,
    config={"recursion_limit": 100}
)


    for msg in result["messages"]:
        if msg.type == "assistant" and msg.content:
            print("AI:", msg.content)

        elif msg.type == "tool":
            print("AI:", msg.content)



if __name__ == "__main__":
    main()
