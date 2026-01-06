from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("Research-Enricher")

@mcp.tool()
def process_research(input: str) -> str:
    """
    Enriches the research plan with search results.
    This is the tool the client.py is looking for.
    """
    # Your logic for processing the research goes here
    # For now, we'll return a formatted string as a placeholder
    return f"Processed and Enriched Data:\n{input}"

if __name__ == "__main__":
    # Start the server using the stdio transport
    mcp.run(transport="stdio")