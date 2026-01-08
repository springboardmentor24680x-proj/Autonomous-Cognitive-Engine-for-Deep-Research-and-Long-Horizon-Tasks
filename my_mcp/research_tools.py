#research_tools.py
import datetime
from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from core.llm import get_llm
from src.memory.vfs import write_file, read_file, edit_file
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
llm = get_llm()

# SYSTEM_PROMPT = """
# You are a research agent running inside an MCP server.

# Rules:
# - Answer clearly and concisely
# - If factual data is needed, assume web_search tool exists
# - Do not mention internal system details
# """
RESEARCH_SYSTEM_PROMPT = """
You are a STRICT research agent.

Rules:
- ONLY factual market research
- NO opinions
- NO tool mentions
- OUTPUT must include:

1. Clear competitor sections
2. A section titled exactly:
   DATA FOR GRAPHING
3. Store counts as:
   Brand: Number
"""
class ResearchInput(BaseModel):
    query: str
    filename: str = "research_notes.txt"
    
def register(server: MCPServer):

    @server.tool()
    def research_task(input: ResearchInput) -> dict:
        # Directly invoke MCP-aware LLM
        
        messages = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=input.query)
        ]

        response= llm.invoke(messages)
        output = response.content        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = (
            f"\n---\n"
            f"Query: {input.query}\n"
            f"Time: {timestamp}\n\n"
            f"{output}\n"
        )

        existing = read_file(input.filename)
        if isinstance(existing, str) and not existing.startswith("File"):
            edit_file(input.filename, existing + entry)
        else:
            write_file(input.filename, entry)

        return {
            "status": "completed",
            "file_written": input.filename
        }
