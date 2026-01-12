from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
import os
def build_planner_agent():
    planner_llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.1
    )

    planner_prompt = """
You are a PLANNER SCRATCHPAD AGENT.

STRICT RULES:
- You NEVER call tools
- You NEVER execute actions
- You ONLY produce a PLAN
- Each step MUST be exactly ONE tool call
- Output MUST be deterministic and machine-readable
- NO explanations, NO markdown, NO prose

Available tools (signatures only):

research_task(description: str, filename: str)
create_visualization(source_file: str, chart_type: str)
write_file(filename: str, content: str)
add_event(title: str, time: str)

OUTPUT FORMAT (MANDATORY):

PLAN:
1. tool_name(arg="...", arg="...")
2. tool_name(arg="...", arg="...")

If information is missing, output:
PLAN:
1. ask_user(question="...")

Do NOT invent tools.

"""

    def plan(user_input: str) -> str:
        return planner_llm.invoke([
            SystemMessage(content=planner_prompt),
            HumanMessage(content=user_input)
        ]).content

    return plan
