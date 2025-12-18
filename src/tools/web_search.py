from langchain_core.tools import tool

# Mocked search result
SEARCH_RESULT = """
Model Context Protocol (MCP) is an open standard developed by Anthropic.
It standardizes how AI models exchange context with tools, databases,
and external systems, enabling better interoperability and context sharing.
"""

@tool
def web_search(query: str) -> str:
    """Search the web for a topic and return results."""
    return SEARCH_RESULT