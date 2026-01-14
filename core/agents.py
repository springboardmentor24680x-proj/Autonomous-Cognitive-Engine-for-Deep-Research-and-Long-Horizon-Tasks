#agents.py
from subagents.research_subagent import build_research_agent
from subagents.summarization_subagent import build_summarization_agent
from src.tools.web_search import web_search
from core.llm import get_llm

llm = get_llm()

research_agent = build_research_agent(llm, tools=[web_search])
summarization_agent = build_summarization_agent(llm)
