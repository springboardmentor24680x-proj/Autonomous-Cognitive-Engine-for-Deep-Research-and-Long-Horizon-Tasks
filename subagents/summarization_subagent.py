from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

SUMMARY_PROMPT = """
You are a summarization sub-agent.

Your ONLY task:
- Summarize the provided content clearly and concisely
- Do NOT add new information
- Do NOT perform research
"""

def build_summarization_agent(groq_client):
    return create_agent(
        model=groq_client,
        tools=[],
        system_prompt=SUMMARY_PROMPT
    )
