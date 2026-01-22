"""Tavily Search Tool - Phase 3 Enhancement"""
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Optional

class TavilySearchTool:
    def __init__(self):
        self.tool = None
        # Check if API Key is available immediately
        if os.getenv("TAVILY_API_KEY"):
            self.tool = TavilySearchResults(max_results=3)
        else:
            print("WARNING: TAVILY_API_KEY not found. Search disabled.")
    
    def search(self, query: str) -> Optional[str]:
        """Tavily web search"""
        if self.tool:
            try:
                return self.tool.invoke({"query": query})
            except Exception as e:
                return f"Search Error: {str(e)}"
        return "Tavily disabled - using LLM research"
    
    def enable(self, api_key: str):
        """Enable Tavily for Phase 3"""
        os.environ["TAVILY_API_KEY"] = api_key
        self.tool = TavilySearchResults(max_results=3)

tavily_tool = TavilySearchTool()
