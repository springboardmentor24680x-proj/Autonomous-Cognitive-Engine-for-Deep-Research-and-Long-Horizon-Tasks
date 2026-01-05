import datetime
from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from core.llm import get_llm
from src.memory.vfs import write_file, read_file, edit_file
from langchain_core.messages import HumanMessage

llm = get_llm()

class ResearchInput(BaseModel):
    query: str
    filename: str = "research_notes.txt"
    
def register(server: MCPServer):

    @server.tool()
    def research_task(input: ResearchInput) -> dict:
        # Directly invoke MCP-aware LLM
        
        response= llm.invoke(input.query)
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
