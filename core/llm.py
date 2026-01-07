import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY missing")

    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )
