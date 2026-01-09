# mcp_client/client.py - FIXED VERSION (no ToolCallResult)
import asyncio
import os
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_SCRIPT = os.path.join(BASE_DIR, "mcp_server", "server.py")

async def _call_mcp(text: str, tool_name: str = "process_research") -> Dict[str, Any]:
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=os.environ.copy()
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(tool_name, arguments={"input": text})
                
                # Simple extraction - works with all MCP versions
                if hasattr(response, 'content') and response.content:
                    output = response.content[0].text if response.content else str(response)
                else:
                    output = str(response)
                    
                return {"output": output, "success": True}
    except Exception as e:
        return {"error": f"MCP Error: {str(e)}", "success": False}

def call_mcp_sync(text: str, tool_name: str = "process_research") -> Dict[str, Any]:
    try:
        return asyncio.run(_call_mcp(text, tool_name))
    except Exception as e:
        return {"error": f"Runtime Error: {str(e)}", "success": False}
