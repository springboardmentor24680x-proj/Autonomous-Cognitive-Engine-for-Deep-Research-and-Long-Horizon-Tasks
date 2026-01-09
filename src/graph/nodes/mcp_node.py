# src/graph/nodes/mcp_node.py - FIXED VERSION
from typing import Dict, Any
from langsmith import traceable
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage
from mcp_client.client import call_mcp_sync

@traceable(name="mcp_node")
def mcp_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fixed MCP node - no config parameter."""
    if not state.get("messages"):
        return {"messages": state["messages"]}

    last_msg = state["messages"][-1]
    user_input = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    tool_name = state.get("tool_name", "process_research")

    mcp_result = call_mcp_sync(user_input, tool_name)
    
    if mcp_result.get("success", False):
        content = f"[{tool_name.upper()}] {mcp_result['output']}"
    else:
        content = f"❌ Error in {tool_name}: {mcp_result.get('error', 'Unknown error')}"

    return {
        "messages": add_messages(state["messages"], AIMessage(content=content)),
        "mcp_result": mcp_result,
        "tool_used": tool_name
    }
