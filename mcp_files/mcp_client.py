import asyncio
import json
import os
import logging
from mcp import ClientSession
from mcp.client.sse import sse_client

# --- LOGGING SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, "mcp_client.log")

logger = logging.getLogger("MCP_Client")

# Avoid adding multiple handlers if this module is imported multiple times
if not logger.handlers:
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

logger.info("MCP Client logger initialized successfully")

# --- SERVER CONFIG ---
SERVER_URL = "http://127.0.0.1:8000/sse"

# --- ASYNC MCP CALL ---
async def _call_mcp(tool_name: str, args: dict):
    """Connects to the ALREADY RUNNING server and calls a tool."""
    logger.info(f"Calling tool: {tool_name} with args: {args}")
    try:
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(tool_name, args)
                res_text = response.content[0].text if response.content else ""
                logger.info(f"Successfully received response from {tool_name}")
                return res_text
    except Exception as e:
        logger.error(f"MCP Connection Error: {str(e)}", exc_info=True)
        return f"Error connecting to MCP server: {str(e)}"

# --- SYNC BRIDGE ---
def call_mcp_sync(tool_name: str, args: dict):
    """Bridge for Streamlit or other sync code to call the SSE server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_call_mcp(tool_name, args))
    finally:
        loop.close()
