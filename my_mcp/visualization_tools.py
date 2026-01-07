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
        
        # Regex to find: Brand: Number
        # Looks specifically for the section 'DATA FOR GRAPHING'
        data_match = re.search(r"DATA FOR GRAPHING\s*([\s\S]*)", content)
        if not data_match:
            return {"error": "Could not find DATA FOR GRAPHING section in file."}
            
        data_text = data_match.group(1)
        data_points = re.findall(r"([\w\s]+):\s*(\d+)", data_text)
        
        if not data_points:
            return {"error": "No data found. Ensure format is 'Brand: Number'."}
            
        labels, values = zip(*[(k.strip(), int(v)) for k, v in data_points])
        
        # Create the Plot
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color=['#8B4513', '#D2691E', '#00704A'])
        plt.title('Market Store Comparison')
        plt.ylabel('Number of Stores')
        
        # Save plot to VFS (Simulated)
        plt.savefig(input.output_image)
        plt.close()
        
        return {
            "status": "Chart created successfully",
            "image_file": input.output_image,
            "data_captured": dict(zip(labels, values))
        }