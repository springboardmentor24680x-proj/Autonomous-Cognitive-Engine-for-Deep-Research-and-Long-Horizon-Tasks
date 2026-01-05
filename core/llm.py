import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

load_dotenv()

SYSTEM_PROMPT = """
You are an autonomous agent running inside an MCP (Model Context Protocol) server.

You do NOT have built-in abilities.
ALL actions (files, research, charts, calendar events) MUST be done using MCP tools.

Rules:
- Never say you cannot do something if a tool exists
- Never mention ChatGPT limitations
- Always prefer calling a tool over explaining
- Assume MCP tools are available and callable
- When asked to list tools, call the list_tools MCP tool
"""

def get_llm():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY missing")

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )

    # Inject system message
    llm = llm.bind(
        messages=[SystemMessage(content=SYSTEM_PROMPT)]
    )

    return llm
