from langchain.tools import tool

@tool
def search_tool(query: str) -> str:
    """Simulated external search tool"""
    return f"Search results for: {query}"
