import re
import matplotlib.pyplot as plt
from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from src.memory.vfs import read_file, write_file

class VisualizationInput(BaseModel):
    filename: str = "research_notes.txt"
    output_image: str = "coffee_market_chart.png"

def register(server: MCPServer):

    @server.tool()
    def create_visualization(input: VisualizationInput) -> dict:
        content = read_file(input.filename)

        match = re.search(r"DATA FOR GRAPHING([\s\S]*)", content)
        if not match:
            return {"error": "DATA FOR GRAPHING section missing"}

        data = re.findall(r"([\w\s]+):\s*(\d+)", match.group(1))
        if not data:
            return {"error": "No graphable data found"}

        labels, values = zip(*[(k.strip(), int(v)) for k, v in data])

        plt.figure(figsize=(8, 5))
        plt.bar(labels, values)
        plt.ylabel("Stores")
        plt.title("Market Comparison")

        plt.savefig(input.output_image)
        plt.close()

        with open(input.output_image, "rb") as f:
            write_file(input.output_image, f.read())

        return {
            "status": "chart_created",
            "image_file": input.output_image
        }
