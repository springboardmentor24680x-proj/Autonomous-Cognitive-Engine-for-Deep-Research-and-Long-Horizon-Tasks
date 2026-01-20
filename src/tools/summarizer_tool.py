from langchain_core.tools import tool
from langsmith import traceable
from langchain_core.messages import SystemMessage, HumanMessage

from tools.llm_factory import make_llm


SUMMARY_PROMPT = """
You are a summarization sub-agent.

Rules:
- Summarize the provided content clearly and concisely
- Do NOT add new information
- Do NOT perform research
- Preserve key facts and structure
"""


@tool
@traceable(name="summarizer")
def summarizer(text: str) -> str:
    """
    Summarizes the given text.
    Input: text (str)
    Output: concise summary
    """
    llm = make_llm()

    messages = [
        SystemMessage(content=SUMMARY_PROMPT),
        HumanMessage(content=text)
    ]

    response = llm.invoke(messages)
    return response.content
