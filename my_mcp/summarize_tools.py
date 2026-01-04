from my_mcp.server.fastapi import MCPServer
from core.agents import summarization_agent
from src.memory.vfs import read_file, write_file

def register(server: MCPServer):

    @server.tool()
    def summarize_file(filename: str) -> dict:
        content = read_file(filename)

        if content.startswith("File"):
            return {"error": content}

        result = summarization_agent.invoke({"input": content})
        summary = result if isinstance(result, str) else result.content

        out = filename.replace(".txt", "_summary.txt")
        write_file(out, summary)

        return {"status": "completed", "summary_file": out}
