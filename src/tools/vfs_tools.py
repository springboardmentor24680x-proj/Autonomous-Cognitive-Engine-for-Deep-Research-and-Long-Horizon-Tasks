from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize free search tool (No API Key Required)
ddg_search = DuckDuckGoSearchRun()

@tool
def write_file(filename: str, content: str):
    """Saves content to the virtual file system (VFS)."""
    return {"action": "write", "filename": filename, "content": content}

@tool
def read_file(filename: str):
    """Reads content from the virtual file system (VFS)."""
    return {"action": "read", "filename": filename}

@tool
def ls_files():
    """Lists all filenames currently stored in the VFS."""
    return {"action": "ls"}

@tool
def write_todos(tasks: list[str]):
    """Decomposes a complex request into a list of sub-tasks."""
    return {"action": "todo", "tasks": tasks}

@tool
def web_search(query: str):
    """Searches the web for real-time information using DuckDuckGo."""
    return ddg_search.run(query)