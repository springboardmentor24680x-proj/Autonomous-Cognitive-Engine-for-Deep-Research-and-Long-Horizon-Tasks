from my_mcp.server.fastapi import MCPServer
from my_mcp import vfs_tools, research_tools, summarize_tools, mcp_calendar_tools
from my_mcp import visualization_tools
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json

# --------------------
# Server
# --------------------
server = MCPServer("autonomous-cognitive-engine")
llm = get_llm()

# --------------------
# Register tools
# --------------------
vfs_tools.register(server)
research_tools.register(server)
summarize_tools.register(server)
mcp_calendar_tools.register_calendar_tools(server)
visualization_tools.register(server)

@server.tool()
def list_tools():
    return server.list_tool_names()

# --------------------
# Supervisor
# --------------------
SUPERVISOR_PROMPT = """
You are a STRICT MCP SUPERVISOR.

You must choose EXACTLY ONE next action.

Available tools:
- research_task
- create_visualization
- add_event
- vfs_read
- vfs_ls

Rules:
- ONE tool per step
- NO explanations
- NO markdown
- Return JSON only in this format:

{
  "action": "<tool_name>",
  "args": { ... }
}
"""

@server.tool()
def supervisor(query: str) -> dict:
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=query)
    ])

    try:
        return json.loads(response.content)
    except Exception as e:
        return {
            "error": "Supervisor output was not valid JSON",
            "raw": response.content
        }

# --------------------
# Run server
# --------------------
if __name__ == "__main__":
    server.run(port=3333)
