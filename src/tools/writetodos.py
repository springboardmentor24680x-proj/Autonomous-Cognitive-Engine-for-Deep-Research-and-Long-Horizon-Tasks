from typing import Dict
from langsmith import traceable
from src.tools.vfs import VFS


@traceable(name="write_todos_tool", run_type="chain")
def write_todos(state: Dict, call_llm) -> Dict:
    """
    call_llm is injected from agent.py
    NO imports from agent.py (prevents circular import)
    """

    vfs = VFS.from_dict(state["vfs"])
    existing = vfs.read_file("intermediary_todos.txt", traced=True)

    prompt = f"""
Maintain an INTERNAL TODO list.

Existing TODOs:
{existing if existing else "(none)"}

New instruction:
{state["input"]}

Rules:
- Never delete existing tasks
- Add missing steps if needed
- Bullet points only
"""

    todos = call_llm([{"role": "user", "content": prompt}])
    vfs.write_file("intermediary_todos.txt", todos)

    state["vfs"] = vfs.to_dict()
    return state
