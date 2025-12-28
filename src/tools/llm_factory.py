import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def make_llm(
    model: str | None = None,
    temperature: float = 0.2,
    timeout: int = 60,
):
    """
    Centralized LLM factory.
    """
    return ChatOpenAI(
        model=model or "gpt-4o-mini",
        temperature=temperature,
        timeout=timeout,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
