from my_mcp.server.fastapi import MCPServer 

# 2. Fix the paths to your tool modules (they are inside mcp/server/)
from mcp.server import vfs_tools, research_tools, summarize_tools, mcp_calendar_tools as calendar_tools

server = MCPServer("autonomous-cognitive-engine")

# 3. Register the tools using the corrected module names
vfs_tools.register(server)
research_tools.register(server)
summarize_tools.register(server)
calendar_tools.register_calendar_tools(server) # Note: ensure function name matches mcp_calendar_tools.py

if __name__ == "__main__":
    server.run(port=3333)