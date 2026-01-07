from langsmith import traceable
from agents.summarization_agent import summarization_agent
from agents.web_search_agent import web_search_agent

SUB_AGENT_REGISTRY = {
    "summarize": summarization_agent,
    "web_search": web_search_agent
}

@traceable(
    name="Task-Delegation-Tool",
    tags=["delegation", "sub-agent", "milestone3"]
)
def delegate_task(task_type: str, task_input: str) -> str:
    agent = SUB_AGENT_REGISTRY.get(task_type)
    if not agent:
        return f" No sub-agent registered for task type: {task_type}"

    try:
        return agent(task_input)
    except Exception as e:
        return f" Sub-agent execution failed: {str(e)}"
