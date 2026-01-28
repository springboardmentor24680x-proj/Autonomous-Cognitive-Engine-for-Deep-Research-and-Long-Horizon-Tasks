from langchain.tools import tool

@tool
def write_file(path: str, content: str, files: dict) -> dict:
    """Write data into the virtual file system"""
    files[path] = content
    return files
