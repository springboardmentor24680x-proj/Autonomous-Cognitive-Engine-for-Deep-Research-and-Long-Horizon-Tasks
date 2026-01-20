# tools/llm_factory.py

import os
from langchain_openai import ChatOpenAI


def make_llm():
    """
    LangChain ChatModel configured for OpenRouter.
    Supports:
    - llm.invoke()
    - LangGraph
    - LangSmith tracing
    """

    return ChatOpenAI(
        model="openai/gpt-4o-mini",  # OpenRouter model ID
        temperature=0.2,

        # 🔑 OpenRouter config
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",

        # Optional but recommended (OpenRouter headers)
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Deep-Agent-LangGraph"
        }
    )
