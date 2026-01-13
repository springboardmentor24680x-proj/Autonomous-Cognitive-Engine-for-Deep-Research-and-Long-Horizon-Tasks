from typing import List, Dict
from langchain_core.messages import HumanMessage
from tools.llm_factory import make_llm


def write_todos(user_goal: str) -> List[Dict[str, str]]:
    """
    Breaks a high-level user goal into structured TODO items.
    Returns a list of dicts with id, task, and status.
    """
    llm = make_llm()

    prompt = HumanMessage(
        content=(
            "Decompose the following goal into clear, ordered TODO tasks.\n"
            "Return each task as a short actionable sentence.\n\n"
            f"GOAL:\n{user_goal}"
        )
    )

    response = llm.invoke([prompt])

    # Simple parsing: one task per line
    todos = []
    for idx, line in enumerate(response.content.splitlines(), start=1):
        line = line.strip("-• ").strip()
        if line:
            todos.append({
                "id": idx,
                "task": line,
                "done": False
            })

    return todos
