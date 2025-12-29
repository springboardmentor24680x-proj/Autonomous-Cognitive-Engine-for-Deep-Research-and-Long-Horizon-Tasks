#!/usr/bin/env python3
"""
Search Tool - Web search and information gathering
Part of the multi-agent workflow automation system
"""

import os
from typing import Dict, Any, List
from langchain_core.tools import tool
from datetime import datetime


@tool
def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for current information using Tavily API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        Dict with search results and metadata
    """
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if Tavily API key is available and valid
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        # Check if key is properly configured (not masked with asterisks)
        if not tavily_api_key or "*" in tavily_api_key or tavily_api_key.startswith("tvly-dev-***"):
            # Use simulated results when API key is not properly configured
            return _simulate_search_results(query, max_results)
        
        # Try to use real Tavily API
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"  # Use basic instead of advanced for better reliability
            )
            
            # Format results
            formatted_results = []
            for result in response.get("results", []):
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")[:500] + "..." if len(result.get("content", "")) > 500 else result.get("content", ""),
                    "score": result.get("score", 0)
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "source": "Tavily API",
                "timestamp": datetime.now().isoformat(),
                "message": f"Found {len(formatted_results)} real search results for '{query}'"
            }
            
        except ImportError:
            # Fallback to simulated results if Tavily package not installed
            return _simulate_search_results(query, max_results)
        except Exception as e:
            # If Tavily API fails, fallback to simulated results
            print(f"Tavily API error: {e}")  # Debug log
            return _simulate_search_results(query, max_results)
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Search failed: {str(e)}"
        }


def _simulate_search_results(query: str, max_results: int) -> Dict[str, Any]:
    """
    Simulate search results when real API is not available.
    
    Args:
        query: Search query
        max_results: Maximum results to simulate
        
    Returns:
        Dict with simulated search results
    """
    # Generate realistic simulated results based on query
    simulated_results = []
    
    # Common search result patterns
    result_templates = [
        {
            "title": f"{query.title()} - Complete Guide and Overview",
            "url": f"https://example.com/{query.lower().replace(' ', '-')}-guide",
            "content": f"Comprehensive information about {query}. This resource covers the latest developments, best practices, and key insights related to {query}.",
            "score": 0.95
        },
        {
            "title": f"Latest News and Updates on {query.title()}",
            "url": f"https://news.example.com/{query.lower().replace(' ', '-')}-news",
            "content": f"Recent news and developments in {query}. Stay updated with the latest trends, announcements, and industry insights.",
            "score": 0.88
        },
        {
            "title": f"{query.title()} - Research and Analysis",
            "url": f"https://research.example.com/{query.lower().replace(' ', '-')}-analysis",
            "content": f"In-depth research and analysis of {query}. Expert insights, data analysis, and comprehensive coverage of key topics.",
            "score": 0.82
        }
    ]
    
    # Select results based on max_results
    for i in range(min(max_results, len(result_templates))):
        simulated_results.append(result_templates[i])
    
    return {
        "success": True,
        "query": query,
        "results": simulated_results,
        "count": len(simulated_results),
        "source": "Simulated (Tavily API key not configured)",
        "timestamp": datetime.now().isoformat(),
        "message": f"Generated {len(simulated_results)} simulated results for '{query}'. Configure TAVILY_API_KEY for real search results."
    }


@tool
def search_news(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Search for recent news articles related to the query.
    
    Args:
        query: News search query
        max_results: Maximum number of news articles to return
        
    Returns:
        Dict with news search results
    """
    # Add "news" to the query for better news-focused results
    news_query = f"{query} news recent"
    return web_search(news_query, max_results)


@tool
def search_academic(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Search for academic and research content related to the query.
    
    Args:
        query: Academic search query
        max_results: Maximum number of academic results to return
        
    Returns:
        Dict with academic search results
    """
    # Add academic terms to the query
    academic_query = f"{query} research academic study"
    return web_search(academic_query, max_results)


def search_with_filters(query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search with additional filters and parameters.
    
    Args:
        query: Search query
        filters: Dictionary of search filters
        
    Returns:
        Dict with filtered search results
    """
    try:
        # Extract filter parameters
        max_results = filters.get("max_results", 5)
        time_range = filters.get("time_range", "any")
        content_type = filters.get("content_type", "any")
        
        # Modify query based on filters
        modified_query = query
        
        if time_range == "recent":
            modified_query += " recent latest"
        elif time_range == "past_year":
            modified_query += " 2024 2025"
        
        if content_type == "news":
            modified_query += " news"
        elif content_type == "academic":
            modified_query += " research study"
        
        return web_search(modified_query, max_results)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Filtered search failed: {str(e)}"
        }


def get_search_suggestions(query: str) -> List[str]:
    """
    Generate search suggestions based on the query.
    
    Args:
        query: Original search query
        
    Returns:
        List of suggested search queries
    """
    suggestions = [
        f"{query} latest trends",
        f"{query} best practices",
        f"{query} how to guide",
        f"{query} comparison analysis",
        f"{query} industry insights"
    ]
    
    return suggestions[:3]  # Return top 3 suggestions