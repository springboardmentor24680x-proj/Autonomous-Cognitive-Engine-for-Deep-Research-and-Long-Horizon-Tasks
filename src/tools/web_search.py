# src/tools/web_search.py

import os
from langchain_core.tools import tool
from langsmith import traceable
from tavily import TavilyClient


@tool
@traceable(name="web_search")
def web_search(query: str) -> str:
    """
    Search the web using Tavily and return clean textual results.
    """

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    response = client.search(
        query=query,
        max_results=5,
        include_raw_content=False
    )

    results = []

    for item in response.get("results", []):
        title = item.get("title", "")
        content = item.get("content", "")
        url = item.get("url", "")

        results.append(
            f"Title: {title}\n"
            f"Content: {content}\n"
            f"Source: {url}"
        )

    if not results:
        return "No results found."

    return "\n\n".join(results)
