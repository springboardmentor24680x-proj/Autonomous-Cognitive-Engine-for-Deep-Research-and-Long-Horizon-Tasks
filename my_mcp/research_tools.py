import datetime
from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from core.agents import research_agent
from src.memory.vfs import write_file, read_file, edit_file

# 1. Define the input schema
class ResearchInput(BaseModel):
    query: str
    filename: str = "research_notes.txt"

def register(server: MCPServer):

    @server.tool()
    def research_task(input: ResearchInput) -> dict:  # 2. Use the schema here
        # Access fields through the input object
        result = research_agent.invoke(
            {"messages": [{"role": "user", "content": input.query}]}
        )

        output = result["messages"][-1].content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = f"\n---\nQuery: {input.query}\nTime: {timestamp}\n\n{output}\n"

        # 3. Adhere to specified filename
        existing = read_file(input.filename)
        if isinstance(existing, str) and not existing.startswith("File"):
            edit_file(input.filename, existing + entry)
        else:
            write_file(input.filename, entry)

        return {"status": "completed", "file_written": input.filename}