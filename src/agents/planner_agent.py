from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

def build_planner_agent(create_work_todo_tool):
    """
    Planner agent:
    - Takes a complex user request
    - Breaks it into ordered TODO subtasks
    - Writes TODOs using create_work_todo
    """

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.2
    )

    SYSTEM_PROMPT = """
You are a PLANNING AGENT.

Your ONLY responsibility:
1. Analyze the user's request
2. Break it into a clear, ordered list of TODO subtasks
3. Each TODO must be a short action-oriented sentence

Rules:
- Do NOT execute tasks
- Do NOT summarize or research
- Do NOT explain
- Output ONLY a numbered TODO list
"""

    def plan(user_request: str):
        response = llm.invoke([
            HumanMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_request)
        ])

        todos = response.content.split("\n")

        for todo in todos:
            todo = todo.strip()
            if todo and todo[0].isdigit():
                task = todo.split(".", 1)[1].strip()
                create_work_todo_tool.invoke({
                    "task_text": task,
                    "status": "PENDING"
                })

        return "Planning completed. TODO list created."

    return plan
