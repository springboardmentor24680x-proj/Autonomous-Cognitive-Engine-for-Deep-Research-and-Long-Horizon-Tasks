from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.tools.web_search import web_search
from langchain_core.tools import tool


# @tool
# def web_search(query: str) -> str:
#     """Search the web for information."""
#     return f"Mock web result for: {query}"


RESEARCH_PROMPT = """
You are a research sub-agent.

CRITICAL RULES (NON-NEGOTIABLE):
- The ONLY tool you are allowed to call is: web_search
- You MUST NOT call glob, grep, ls, read_file, or any filesystem tool
- You MUST NOT invent tools
- You MUST NOT search local files
- Call web_search AT MOST once
- If the tool fails, answer using general knowledge

Produce a factual, structured research answer.
"""



def build_research_agent(groq_client):
    return create_agent(
        model=groq_client,
        tools=[web_search],
        system_prompt=RESEARCH_PROMPT,
    )
