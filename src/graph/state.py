from typing import TypedDict

class AgentState(TypedDict, total=False):
    query: str
    todos: str
    research: str
    summary: str
    files_written: bool
