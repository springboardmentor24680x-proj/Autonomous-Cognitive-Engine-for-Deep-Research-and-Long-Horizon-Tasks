from langchain_core.tools import tool
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)


@tool
def summarize_text(text: str) -> str:
    """Summarize text into two concise sentences."""
    res = llm.invoke(
        f"Summarize the following in two concise sentences:\n{text}"
    )
    return res.content
