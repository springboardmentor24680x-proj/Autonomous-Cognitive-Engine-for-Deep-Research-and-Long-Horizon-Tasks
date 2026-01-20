# src/agents/planner_agent.py

from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

from tools.llm_factory import make_llm


PLANNER_SYSTEM_PROMPT = """
You are a STRICT PLANNER AGENT.

RULES:
- For every user request, you MUST generate a TODO list.
- Break tasks into clear, ordered, interlinked TODOs.
- Each TODO must map to an available agent or tool.
- Do NOT execute tasks.
- Do NOT summarize, research, or write files yourself.
- Output ONLY JSON.
- NO explanations. NO markdown.

AVAILABLE ACTIONS:
- web_search
- summarizer
- write_file
- read_file

Output format (JSON ONLY):
{
  "todos": [
    {
      "id": "todo-1",
      "action": "<action_name>",
      "description": "<what needs to be done>",
      "depends_on": []
    }
  ]
}
"""


@traceable(name="planner_agent")
def planner_node(state: Dict) -> Dict:
    """
    Planner node for LangGraph.
    Produces ONLY a TODO list.
    """
    llm = make_llm()

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=state["query"])
    ]

    response = llm.invoke(messages)

    # Planner ONLY adds todos to state
    state["todos"] = response.content

    return state
