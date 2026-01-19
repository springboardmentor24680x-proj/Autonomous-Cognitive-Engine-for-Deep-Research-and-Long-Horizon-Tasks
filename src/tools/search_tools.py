from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

def get_resources(query: str):
    # This returns a string of snippets and links
    return search_tool.run(query)