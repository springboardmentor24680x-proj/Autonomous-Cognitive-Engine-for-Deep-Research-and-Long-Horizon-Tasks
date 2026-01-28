from langchain.tools import tool

@tool
def read_file(path: str, files: dict) -> str:
    """Read data from the virtual file system"""
    return files.get(path, "")
