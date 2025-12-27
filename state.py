from typing import TypedDict, List, Any

class AgentState(TypedDict):
    messages: List[Any]
    search_results: str
    next_node: str
