from langsmith import traceable
from langchain_groq import ChatGroq

class WebSearchTool:

    @traceable(name="Web Search Tool", run_type="tool")
    def run(self, query: str) -> str:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        res = llm.invoke(
            f"""
Search IT-related sources and return structured info with sources.

Query: {query}

Include:
- Facts
- Sources (docs, blogs, papers)
"""
        )
        return res.content
