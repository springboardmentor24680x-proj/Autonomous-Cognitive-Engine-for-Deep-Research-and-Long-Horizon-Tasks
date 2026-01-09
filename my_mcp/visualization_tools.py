import matplotlib.pyplot as plt
import base64
from io import BytesIO
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP):

    @mcp.tool()
    def create_visualization(data: dict):
        brands = list(data.keys())
        values = list(data.values())

        plt.figure()
        plt.bar(brands, values)

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()

        encoded = base64.b64encode(buf.getvalue()).decode()
        return {"image_base64": encoded}
