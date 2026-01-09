def router_node(state):
    """
    Simple router: sends research queries to MCP
    """
    user_query = state["messages"][-1].content.lower()

    if "research" in user_query or "deep" in user_query:
        return "mcp"

    return "mcp"   # default → MCP for now
