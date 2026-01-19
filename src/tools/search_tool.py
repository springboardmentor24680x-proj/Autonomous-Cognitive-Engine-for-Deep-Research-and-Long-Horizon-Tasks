from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def search_tool(query: str):
    """Searches the web using DuckDuckGo for real-time information."""
    try:
        return DuckDuckGoSearchRun().run(query)
    except Exception as e:
        return f"Search error: {str(e)}"