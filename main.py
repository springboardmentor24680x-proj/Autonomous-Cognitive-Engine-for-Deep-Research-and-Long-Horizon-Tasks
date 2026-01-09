from my_mcp.server.fastapi import MCPServer
from my_mcp import vfs_tools, research_tools, summarize_tools, mcp_calendar_tools, visualization_tools
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json
import logging
import os

# --------------------
# Logging Setup
# --------------------
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("MCP_SERVER")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler("logs/main.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --------------------
# Server Initialization
# --------------------
logger.info("Initializing MCP Server")
server = MCPServer("autonomous-cognitive-engine")
llm = get_llm()

# --------------------
# Register Tools
# --------------------
logger.info("Registering tools")

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
You are a SUPERVISOR.

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
  "args": { }
}
"""

@server.tool()
def supervisor(state: dict) -> dict:
    logger.info(f"Supervisor called | state={state}")

    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=json.dumps(state))
    ])

    logger.info(f"LLM raw response: {response.content}")

    try:
        decision = json.loads(response.content)
        logger.info(f"Supervisor decision: {decision}")
        return decision
    except Exception:
        logger.exception("Supervisor JSON parsing failed")
        return {"action": "stop"}

# --------------------
# Run Server
# --------------------
if __name__ == "__main__":
    logger.info("Starting MCP Server on port 3333")
    server.run(port=3333)
