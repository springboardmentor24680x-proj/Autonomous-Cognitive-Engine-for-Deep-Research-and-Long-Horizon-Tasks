#llm.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Singleton LLM instance to avoid redundant instantiation and connection overhead
_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY missing")
        _llm_instance = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.3
        )
    return _llm_instance
