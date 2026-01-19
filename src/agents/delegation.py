from langgraph.graph import END
from typing import Literal

def delegate_task(state: dict) -> Literal["search_agent", "summarizer_agent", "__end__"]:
    """
    Supervisor Delegation Logic:
    Checks the 'todo' list in the shared state and routes to the 
    specialized sub-agent required for the next step.
    """
    todo_list = state.get("todo", [])
    
    # 1. Prioritize Research/Search if it's on the list
    if "Search" in todo_list:
        print("--- DELEGATING: Search_Agent ---")
        return "search_agent"
    
    # 2. If search is done, move to Summarization
    elif "Summarize" in todo_list:
        print("--- DELEGATING: Summarizer_Agent ---")
        return "summarizer_agent"
    
    # 3. If no tasks remain, terminate the workflow
    print("--- DELEGATION COMPLETE: Finishing ---")
    return END