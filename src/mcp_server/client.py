import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define the path to your server.py relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_SCRIPT = os.path.join(BASE_DIR, "mcp_server", "server.py")

async def _call_mcp(text: str):
    # 1. Define the parameters (Fixes the "not defined" error)
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=os.environ.copy()
    )

    try:
        # 2. Use the parameters to start the client
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 3. Call the tool defined in your server.py
                response = await session.call_tool("process_research", arguments={"input": text})
                
                # 4. Extract text from the response content list
                result_text = ""
                if hasattr(response, 'content') and len(response.content) > 0:
                    result_text = response.content[0].text
                else:
                    result_text = str(response)

                # 5. Return a dictionary so supervisor_agent.py can use .get("output")
                return {"output": result_text}
                
    except Exception as e:
        return {"output": f"MCP Client Error: {str(e)}"}

def call_mcp_sync(text: str):
    """Synchronous wrapper for LangGraph nodes."""
    try:
        return asyncio.run(_call_mcp(text))
    except Exception as e:
        return {"output": f"Runtime Error: {str(e)}"}