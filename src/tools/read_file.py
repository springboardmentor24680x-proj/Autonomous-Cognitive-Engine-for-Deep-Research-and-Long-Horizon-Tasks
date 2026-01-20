from langchain_core.tools import tool

@tool
def read_file(filename: str):
    """Read content from a file."""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return f"Content of {filename}: {content[:200]}..."
    except FileNotFoundError:
        return f"File {filename} not found"
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"
