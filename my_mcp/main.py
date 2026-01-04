# main.py (Now in the root directory)
import sys
import os

# Add the current directory to sys.path to ensure 'my_mcp' is found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from my_mcp.server.fastapi import MCPServer 
from my_mcp.server import vfs_tools, research_tools, summarize_tools, mcp_calendar_tools

server = MCPServer("autonomous-cognitive-engine")

# Register tools
vfs_tools.register(server)
research_tools.register(server)
summarize_tools.register(server)
mcp_calendar_tools.register_calendar_tools(server)

if __name__ == "__main__":
    server.run(port=3333)