# src/tools/llm_factory.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def make_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
