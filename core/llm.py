import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

SYSTEM_PROMPT = """
You are an MCP-controlled agent.

You NEVER simulate tools.
You NEVER write tool syntax.
You NEVER write code blocks to execute.

If a task requires:
- files → request vfs tools
- research → request research tools
- charts → request chart tools
- calendar → request calendar tools

You only describe intent.
The MCP server executes tools.

"""

def get_llm():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY missing")

    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )
