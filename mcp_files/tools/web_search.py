import os
from langchain_core.tools import tool
from tavily import TavilyClient

@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time information, news, or deep research data.
    Use this when you need data from 2024 or 2025.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    # We use 'search' with 'include_answer' for a quick summary 
    # or 'advanced' for deeper research.
    response = client.search(query=query, search_depth="advanced", max_results=5)
    
    # Format the results into a clean string for the agent
    context = [f"Source: {obj['url']}\nContent: {obj['content']}" for obj in response['results']]
    return "\n\n---\n\n".join(context)