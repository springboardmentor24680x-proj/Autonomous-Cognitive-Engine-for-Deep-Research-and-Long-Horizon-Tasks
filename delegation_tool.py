# delegation_tool.py

from langchain_core.tools import tool
from agent_registry import get_subagent_registry


def build_task_tool(groq_client):
    registry = get_subagent_registry(groq_client)

    @tool
    def task(description: str, subagent_type: str) -> str:
        """
        Delegate a task to a specialized sub-agent.

        Args:
            description: The task to perform
            subagent_type: Type of sub-agent (e.g. 'research-agent')
        """

        if subagent_type not in registry:
            return f"Unknown sub-agent type: {subagent_type}"

        subagent = registry[subagent_type]

        result = subagent.invoke({
            "messages": [{"role": "user", "content": description}]
        })

        return result["messages"][-1].content

    return task
