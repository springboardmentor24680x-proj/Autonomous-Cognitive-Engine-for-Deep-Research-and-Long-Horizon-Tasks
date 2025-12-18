from langchain_core.tools import tool
from subagents.research_subagent import build_research_agent

@tool
def task(description: str, subagent_type: str) -> str:
    """
    Delegate a task to a sub-agent.
    """

    if subagent_type != "research-agent":
        return f"Unknown sub-agent type: {subagent_type}"

    research_agent = build_research_agent()

    result = research_agent.invoke({
        "messages": [{"role": "user", "content": description}]
    })

    return result["messages"][-1].content
