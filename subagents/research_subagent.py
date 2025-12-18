from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.tools.web_search import web_search

RESEARCH_PROMPT = """
You are a research sub-agent.
Your ONLY job is to research the given topic.
You MUST call the web_search tool exactly once.
Use the tool result to produce a factual answer.
"""

def build_research_agent(groq_client):
    return create_agent(
        model=groq_client,
        tools=[web_search],
        system_prompt=RESEARCH_PROMPT
    )
