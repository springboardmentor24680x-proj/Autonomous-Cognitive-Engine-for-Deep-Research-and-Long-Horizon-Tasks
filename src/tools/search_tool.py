from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web and return relevant factual information.
    """
    # Placeholder implementation (mocked search)
    return (
        "FACT: Microlearning modules are usually 5–10 minutes long "
        "and significantly improve learner engagement."
    )
