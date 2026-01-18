# planner_agent.py
from typing import List, Dict
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from deepagents import create_deep_agent

PLANNER_SYSTEM_PROMPT = """
You are a STRICT PLANNER AGENT.

RULES:
- For every user request, you MUST generate a TODO list.
- Break tasks into clear, ordered, interlinked TODOs.
- Each TODO must map to an available tool or sub-agent.
- Do NOT execute tasks.
- Do NOT summarize, research, visualize, or write files yourself.
- Output ONLY structured TODOs.

AVAILABLE CAPABILITIES:
- web_search
- write_file
- read_file
- edit_file
- create_visualization
- summarization_task
- add_event (calendar)

Output format (JSON ONLY):
{
  "todos": [
    {
      "id": "todo-1",
      "action": "<tool_or_agent_name>",
      "description": "<what needs to be done>",
      "depends_on": []
    }
  ]
}
"""

planner_agent = create_deep_agent(
    name="planner_agent",
    system_message=SystemMessage(content=PLANNER_SYSTEM_PROMPT),
    tools=[],  # planner does NOT execute tools
)

def plan(user_request: str) -> Dict:
    """
    Entry point for planning.
    Returns a TODO plan only.
    """
    return planner_agent.invoke(user_request)
