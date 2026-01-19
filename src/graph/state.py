from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    input: str
    todo: List[str]          # No Annotation = Default Overwrite behavior
    files: Dict[str, str]
    resources: List[str]     # Remove Annotation here too if you want to overwrite
    next_step: str
    is_finished: bool