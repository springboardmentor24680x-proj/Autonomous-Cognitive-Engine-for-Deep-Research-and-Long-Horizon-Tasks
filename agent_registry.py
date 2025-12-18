# agent_registry.py

from subagents.research_subagent import build_research_subagent


def get_subagent_registry(groq_client):
    return {
        "research-agent": build_research_subagent(groq_client),
    }
