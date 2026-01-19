from langchain_core.tools import tool

@tool
def read_file(filename: str) -> str:
    """
    Retrieves the content of a specific file from the virtual workspace.
    Use this when you need to recall information saved in a previous step.
    
    Args:
        filename: The exact name of the file to retrieve.
    """
    # The supervisor node will inject the content from the state 'vfs' dictionary.
    return f"FILE_READ_REQUEST:{filename}"