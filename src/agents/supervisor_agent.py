from langchain_core.tools import tool
from src.agents.search_agent import search_agent
from langchain_core.messages import HumanMessage

@tool
def call_research_agent(query: str):
    """Delegates deep web research and fact-finding to the Research Sub-Agent."""
    try:
        response = search_agent.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content
    except Exception as e:
        return f"Research Delegation Error: {str(e)}"