# src/agents/research_agent.py

from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

from tools.llm_factory import make_llm
from tools.web_search import web_search


RESEARCH_PROMPT = """
You are a research sub-agent.

CRITICAL RULES:
- You may call web_search AT MOST once
- Output MUST be under 250 words
- Use bullet points only
- Each bullet ≤ 2 lines
- No introductions or conclusions

If web_search fails, answer using general knowledge.


Do not include units like '%' or extra words in this section.
"""


@traceable(name="research_agent")
def research_node(state: dict) -> dict:
    """
    Research agent node.
    Uses web_search once and produces structured research output.
    """

    llm = make_llm()
    query = state["query"]

    # --- Web search (single call) ---
    search_results = web_search.invoke({"query": query})

    prompt = f"""
Query:
{query}

Web search results:
{search_results}

Follow ALL rules strictly.
"""

    messages = [
        SystemMessage(content=RESEARCH_PROMPT),
        HumanMessage(content=prompt)
    ]

    response = llm.invoke(messages)

    state["research"] = response.content
    return state
