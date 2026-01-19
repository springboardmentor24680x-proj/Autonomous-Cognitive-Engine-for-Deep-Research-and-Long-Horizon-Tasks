from langchain_core.tools import tool

@tool
def write_file(filename: str, content: str) -> str:
    """
    Saves or updates a file in the virtual workspace. 
    Use this to offload research summaries or final reports.
    
    Args:
        filename: Name of the file (e.g., 'research_summary.txt')
        content: The text content to be saved.
    """
    # The actual saving logic is handled by the state_updater_node in main.py
    return f"File '{filename}' has been successfully written to the workspace."