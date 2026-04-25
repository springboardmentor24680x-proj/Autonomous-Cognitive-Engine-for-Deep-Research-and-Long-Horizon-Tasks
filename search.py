from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str):
    print("🌐 Searching web for:", query)

    response = client.search(query=query, search_depth="basic")

    results = []

    for r in response["results"]:
        results.append(r["content"])

    return "\n\n".join(results[:3])  # top 3 results