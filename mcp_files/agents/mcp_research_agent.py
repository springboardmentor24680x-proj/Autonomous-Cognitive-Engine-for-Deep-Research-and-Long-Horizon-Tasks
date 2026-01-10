from langchain_groq import ChatGroq
from langgraph.prebuilt import create_agent
from tools.web_search import web_search_tool

llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0
)

ResearchAgent = create_agent(
    llm=llm,
    tools=[web_search_tool],
    state_modifier="""
You are a research-only agent.
You must ONLY gather factual information using tools.
Do NOT answer the user directly.
Return findings clearly.
"""
)
