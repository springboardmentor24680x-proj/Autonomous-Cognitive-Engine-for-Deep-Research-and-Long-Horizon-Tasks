from langsmith import traceable
from serpapi import GoogleSearch

import os

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not SERPAPI_API_KEY:
    raise RuntimeError(" SERPAPI_API_KEY is missing in .env")

@traceable(
    name="Web-Search-Agent",
    tags=["sub-agent", "web-search", "milestone3"]
)
def web_search_agent(query: str) -> str:
    """Perform a web search and return summarized results."""

    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": 5
    })

    results = search.get_dict()

    if "organic_results" not in results:
        return " No search results found."

    summaries = []
    for i, item in enumerate(results["organic_results"][:5], 1):
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        summaries.append(f"{i}. **{title}**\n{snippet}\n{link}")

    return "\n\n".join(summaries)
