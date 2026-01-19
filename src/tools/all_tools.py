from langchain_core.tools import tool
from typing import List
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def search_tool(query: str) -> str:
    """
    Search the internet using DuckDuckGo. 
    Use this tool to find real-time information, news, or technical details 
    that are not in your training data.
    Args:
        query: A specific search string.
    """
    search = DuckDuckGoSearchRun()
    try:
        return search.run(query)
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def write_file(filename: str, content: str) -> str:
    """
    Saves text content to a specific file in the Virtual File System (VFS).
    Use this to offload long research notes or save intermediate drafts.
    Args:
        filename: The name of the file (e.g., 'research_notes.txt').
        content: The text data to be saved.
    """
    # The actual state update is handled by the tool_node in main.py
    return f"Successfully saved to {filename}."

@tool
def read_file(filename: str) -> str:
    """
    Retrieves the content of a previously saved file from the VFS.
    Args:
        filename: The exact name of the file to read.
    """
    # The actual retrieval is handled by the tool_node logic in main.py
    return f"Reading {filename}..."

@tool
def write_todos(tasks: List[str]) -> str:
    """
    Decomposes a complex goal into a structured list of sub-tasks.
    This tool should be used at the beginning of a complex request to create a plan.
    Args:
        tasks: A list of strings, each representing a single discrete task.
    """
    return f"Plan updated with {len(tasks)} tasks."