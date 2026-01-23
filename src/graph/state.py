from typing import TypedDict, List, Dict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    final_answer: str
    current_task: str
    todo_status: List[Dict[str, str]]