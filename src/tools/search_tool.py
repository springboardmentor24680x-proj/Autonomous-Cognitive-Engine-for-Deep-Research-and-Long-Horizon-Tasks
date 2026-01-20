"""Tavily Search Tool - Phase 3 Enhancement"""
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Optional

class TavilySearchTool:
    def __init__(self):
        # DISABLED for production stability
        self.tool = None  # TavilySearchResults(max_results=3)
    
    def search(self, query: str) -> Optional[str]:
        """Tavily web search (disabled in production)"""
        if self.tool:
            return self.tool.invoke({"query": query})
        return "Tavily disabled - using LLM research"
    
    def enable(self, api_key: str):
        """Enable Tavily for Phase 3"""
        os.environ["TAVILY_API_KEY"] = api_key
        self.tool = TavilySearchResults(max_results=3)

tavily_tool = TavilySearchTool()
