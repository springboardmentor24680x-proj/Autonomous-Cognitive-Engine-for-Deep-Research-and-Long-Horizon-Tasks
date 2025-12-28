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

CRITICAL RULES:
- You may call web_search AT MOST once
- Output MUST be under 250 words
- Use bullet points only
- Each bullet ≤ 2 lines
- No introductions or conclusions

If web_search fails, answer using general knowledge.
CRITICAL: At the very end of your report, provide a section titled 'DATA FOR GRAPHING'. List only the entities and their numerical shares in this exact format: Starbucks: 30 Nescafe: 45 Do not include units like '%' or extra words in this section

Whenever you find market shares, growth percentages, or financial data, format them at the end of your report in a 'DATA BLOCK' using the format: Label: Value. For example: Starbucks: 25.
"""



def build_research_agent(groq_client):
    return create_agent(
        model=groq_client,
        tools=[web_search],
        system_prompt=RESEARCH_PROMPT,
    )
