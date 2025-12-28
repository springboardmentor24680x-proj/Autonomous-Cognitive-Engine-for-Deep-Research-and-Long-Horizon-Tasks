from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # Conversation history
    messages: List[BaseMessage]

    # Web search output (if any)
    search_results: Optional[str]

    # Router decision flag
    needs_web: Optional[bool]
