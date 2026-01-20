from langchain_core.tools import tool

@tool
def write_file(filename: str, content: str):
    """Write content to a file. Use for saving research results."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Saved to {filename}"
    except Exception as e:
        return f"Error writing {filename}: {str(e)}"
