from my_mcp.server.fastapi import MCPServer 

# 2. Update the paths to your tool modules
from my_mcp import vfs_tools, research_tools, summarize_tools, mcp_calendar_tools

server = MCPServer("autonomous-cognitive-engine")

# 3. Register the tools
vfs_tools.register(server)
research_tools.register(server)
summarize_tools.register(server)
mcp_calendar_tools.register_calendar_tools(server) #

if __name__ == "__main__":
    server.run(port=3333)