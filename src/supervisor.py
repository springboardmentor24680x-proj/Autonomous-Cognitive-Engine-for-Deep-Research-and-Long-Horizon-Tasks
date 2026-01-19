from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    todo_list: List[str]
    vfs: dict
    next_step: str

def supervisor_node(state: AgentState):
    last_msg = state["messages"][-1]
    
    # Route logic
    if hasattr(last_msg, 'name'):
        if last_msg.name == "researcher":
            return {"next_step": "summarizer"}
        if last_msg.name == "summarizer":
            return {"next_step": "end"}
            
    return {"next_step": "researcher"}
