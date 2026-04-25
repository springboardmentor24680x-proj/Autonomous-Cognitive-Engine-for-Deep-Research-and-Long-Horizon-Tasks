from typing import TypedDict, List, Dict


class AgentState(TypedDict, total=False):
    messages: List[dict]          # user + system messages
    todos: List[dict]             # [{"task": str, "status": "pending/done"}]
    current_task: str             # task being executed
    files: Dict[str, str]         # virtual file system (memory)
    final_output: str             # final generated report
    action: str                   # routing signal for LangGraph