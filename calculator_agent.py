from typing import TypedDict, Annotated
import operator
import os

from langchain.tools import tool
from langchain.messages import (
    SystemMessage,
    ToolMessage,
    HumanMessage,
    AIMessage,
    AnyMessage,
)
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq


# ========================================================
# 1) Initialize Groq Model (IMPORTANT FIX HERE)
# ========================================================
model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    max_tokens=500,
    model_kwargs={"tool_choice": "auto"},
)



# ========================================================
# 2) Define Tools
# ========================================================
@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """Divide a by b"""
    return a / b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


tools = [add, multiply, divide, subtract]
tools_by_name = {t.name: t for t in tools}

model_with_tools = model.bind_tools(tools)


# ========================================================
# 3) State Definition
# ========================================================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ========================================================
# 4) LLM Node
# ========================================================
def llm_node(state: AgentState):
    system = SystemMessage(
        content=(
            "You are a calculator assistant. "
            "Always use tools for arithmetic and then return a clear final answer."
        )
    )

    response = model_with_tools.invoke([system] + state["messages"])
    return {"messages": [response]}


# ========================================================
# 5) Tool Node
# ========================================================
def tool_node(state: AgentState):
    last = state["messages"][-1]
    tool_messages = []

    for call in last.tool_calls:
        tool_fn = tools_by_name[call["name"]]
        result = tool_fn.invoke(call["args"])

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
            )
        )

    return {"messages": tool_messages}


# ========================================================
# 6) Routing Logic
# ========================================================
def router(state: AgentState):
    last = state["messages"][-1]

    if isinstance(last, AIMessage) and last.tool_calls:
        return "tool_node"

    return END


# ========================================================
# 7) Build Graph
# ========================================================
builder = StateGraph(AgentState)

builder.add_node("llm_node", llm_node)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm_node")
builder.add_conditional_edges("llm_node", router, ["tool_node", END])
builder.add_edge("tool_node", "llm_node")

agent = builder.compile()


# ========================================================
# 8) Run Agent
# ========================================================
def run_agent(user_input: str) -> str:
    state = {"messages": [HumanMessage(content=user_input)]}
    result = agent.invoke(state)

    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content

    return "No result generated."


# ========================================================
# 9) CLI Entry Point
# ========================================================
if __name__ == "__main__":
    user_text = input("Enter a math request: ").strip()

    if not user_text:
        print("No input provided.")
        exit()

    answer = run_agent(user_text)

    print("\nFinal Answer:")
    print("------------------------")
    print(answer)
