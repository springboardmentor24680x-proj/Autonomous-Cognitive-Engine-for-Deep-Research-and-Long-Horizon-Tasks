from utils.llm import call_llm
from langsmith import traceable

@traceable(
    name="Summarization-Agent",
    tags=["sub-agent", "summarize", "milestone3"]
)
def summarization_agent(text: str) -> str:
    prompt = f"""
Summarize the following content clearly and concisely:

{text}
"""
    return call_llm(prompt)
