from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]

    # Task routing
    intent: Optional[str]

    # Research
    research_query: Optional[str]
    research_file: Optional[str]

    # Summarization
    source_file: Optional[str]
    summary_text: Optional[str]

    # Visualization
    chart_type: Optional[str]
    chart_title: Optional[str]

    # System output
    final_response: Optional[str]
