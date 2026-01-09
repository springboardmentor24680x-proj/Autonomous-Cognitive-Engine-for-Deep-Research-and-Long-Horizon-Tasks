"""
AI Research Agent - Complete Working Implementation
Tavily Search + MCP Tools + VFS Sidebar + LangGraph
"""

import os
import asyncio
import streamlit as st
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# STATE DEFINITION
# =============================================================================
class AgentState(TypedDict):
    messages: List[BaseMessage]
    tool_name: str
    next_node: str

# =============================================================================
# VFS (Virtual File System)
# =============================================================================
class VFS:
    def ls(self) -> list[str]:
        return [
            "research.pdf",
            "market.csv",
            "todos.md",
            "project_plan.docx",
            "q1_2026_earnings.xlsx",
        ]

    def read_file(self, filename: str) -> str:
        contents = {
            "research.pdf": "AI Market Research Report - Jan 2026\nNVDA leads AI chips.",
            "market.csv": "ticker,price\nNVDA,169.2\nMSFT,457.1",
            "todos.md": "- Deploy agent\n- Create dashboard",
            "project_plan.docx": "Phase 1 MVP\nPhase 2 Production",
            "q1_2026_earnings.xlsx": "Revenue: $38.2B\nEPS: $7.45",
        }
        return contents.get(filename, "File not found")

vfs = VFS()

# =============================================================================
# MOCK SERVICES
# =============================================================================
@st.cache_data(ttl=300)
def tavily_search(query: str) -> str:
    return f"""
🔍 **Tavily Search Results**

Query: {query}

• AI market growing rapidly
• NVDA demand +245% YoY
• Enterprise LLM adoption at 78%
"""

async def mock_mcp_call(text: str, tool_name: str) -> Dict[str, Any]:
    await asyncio.sleep(0.3)
    return {
        "success": True,
        "output": f"""
🔬 **MCP TOOL – {tool_name.upper()}**

Input:
{text}

Findings:
• Market strongly bullish
• AI infra spend accelerating
• Recommendation: Proceed
"""
    }

def call_mcp_sync(text: str, tool_name: str) -> Dict[str, Any]:
    return asyncio.run(mock_mcp_call(text, tool_name))

# =============================================================================
# LANGGRAPH NODES
# =============================================================================
@traceable(name="router")
def router_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    if not messages:
        return {**state, "next_node": "search"}

    content = messages[-1].content.lower()

    if any(k in content for k in ["todo", "task", "plan"]):
        next_node = "todo"
    elif any(k in content for k in ["research", "analyze", "market", "data"]):
        next_node = "mcp"
    else:
        next_node = "search"

    return {**state, "next_node": next_node}

@traceable(name="search")
def search_node(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    result = tavily_search(query)

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=result)]
    }

@traceable(name="mcp")
def mcp_node(state: AgentState) -> AgentState:
    text = state["messages"][-1].content
    tool_name = state.get("tool_name", "process_research")

    result = call_mcp_sync(text, tool_name)
    content = result["output"] if result["success"] else "❌ MCP Error"

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=content)]
    }

@traceable(name="todo")
def todo_node(state: AgentState) -> AgentState:
    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content="""
✅ **PROJECT TODO LIST**

1. Deploy LangGraph agent
2. Build dashboard
3. Team review meeting
""")
        ]
    }

@traceable(name="summarize")
def summarize_node(state: AgentState) -> AgentState:
    recent = "\n".join(m.content for m in state["messages"][-3:])
    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content=f"📋 **SUMMARY**\n{recent}")
        ]
    }

# =============================================================================
# LANGGRAPH SETUP
# =============================================================================
def create_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("mcp", mcp_node)
    graph.add_node("todo", todo_node)
    graph.add_node("summarize", summarize_node)

    graph.set_entry_point("router")

    def route_to_node(state: AgentState) -> str:
        node = state.get("next_node", "search")
        return node if node else "search"

    graph.add_conditional_edges(
        "router",
        route_to_node,
        {
            "search": "search",
            "mcp": "mcp",
            "todo": "todo",
        }
    )

    graph.add_edge("search", "summarize")
    graph.add_edge("mcp", "summarize")
    graph.add_edge("todo", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()

agent_graph = create_agent_graph()

# =============================================================================
# STREAMLIT UI
# =============================================================================
st.set_page_config(page_title="AI Research Agent", layout="wide")
st.title("🤖 AI Research Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_name" not in st.session_state:
    st.session_state.tool_name = "process_research"

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

with st.sidebar:
    st.subheader("📁 Virtual File System")
    file = st.selectbox("Select file", vfs.ls())
    if st.button("Read File"):
        st.text(vfs.read_file(file))

    st.subheader("🔬 MCP Tool")
    st.session_state.tool_name = st.selectbox(
        "Tool",
        ["process_research", "analyze_market", "plan_project"]
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append(HumanMessage(content=prompt))

    input_state: AgentState = {
        "messages": st.session_state.messages,
        "tool_name": st.session_state.tool_name,
        "next_node": "",
    }

    result = agent_graph.invoke(input_state)

    st.session_state.messages = result["messages"]
    st.rerun()
