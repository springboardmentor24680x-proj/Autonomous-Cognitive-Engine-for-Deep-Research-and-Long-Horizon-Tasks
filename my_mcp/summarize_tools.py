from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from core.agents import summarization_agent
from src.memory.vfs import read_file, write_file

# 1. Define the input schema
class SummarizeInput(BaseModel):
    filename: str

def register(server: MCPServer):

    @server.tool()
    def summarize_file(input: SummarizeInput) -> dict: # 2. Use the schema here
        # Access the filename through the input object
        content = read_file(input.filename)

        if content.startswith("File"):
            return {"error": content}

        result = summarization_agent.invoke({"input": content})
        summary = result if isinstance(result, str) else result.content

        # Determine the output filename
        out = input.filename.replace(".txt", "_summary.txt")
        write_file(out, summary)

        return {"status": "completed", "summary_file": out}