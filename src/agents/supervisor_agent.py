

# from src.memory.vfs import VFS
# from src.planning.todo import TodoManager

# vfs = VFS()
# todo_manager = TodoManager()


# def agent_step(user_input, state):
#     # Add task once
#     if not state.get("todos"):
#         todo_manager.add(state, [
#             {"task": user_input, "done": False}
#         ])

#     # Execute first pending task
#     for t in state["todos"]:
#         if not t["done"]:
#             state["current_task"] = t["task"]
#             t["done"] = True
#             break

#     # Persist memory
#     vfs.write(state, "conversation.md", state["current_task"])

#     # Respond
#     state["messages"].append({
#         "role": "assistant",
#         "content": f"✅ Completed task: **{state['current_task']}**"
#     })

#     return state




import os
from groq import Groq

from src.memory.vfs import VFS
from src.planning.todo import TodoManager

# -------------------------------------------------
# INIT
# -------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

vfs = VFS()
todo_manager = TodoManager()


# -------------------------------------------------
# SUPERVISOR AGENT (LLM-DRIVEN)
# -------------------------------------------------
def agent_step(user_input, state):
    """
    LLM-powered supervisor reasoning step
    """

    # -------------------------------------------------
    # 1. PLAN TASK (only once)
    # -------------------------------------------------
    if not state.get("todos"):
        todo_manager.add(state, [
            {"task": user_input, "done": False}
        ])

    # -------------------------------------------------
    # 2. PICK NEXT TASK
    # -------------------------------------------------
    current_task = None
    for t in state["todos"]:
        if not t["done"]:
            current_task = t
            break

    if not current_task:
        return state

    # -------------------------------------------------
    # 3. LLM REASONING (Groq)
    # -------------------------------------------------
    prompt = f"""
You are an autonomous AI agent.

Your current task:
{current_task['task']}

Think step-by-step and provide a helpful, clear response.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful autonomous agent."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    llm_output = response.choices[0].message.content

    # -------------------------------------------------
    # 4. UPDATE STATE
    # -------------------------------------------------
    current_task["done"] = True
    state["current_task"] = current_task["task"]

    state["messages"].append({
        "role": "assistant",
        "content": llm_output
    })

    # -------------------------------------------------
    # 5. STORE IMPORTANT MEMORY
    # -------------------------------------------------
    vfs.write(
        state,
        "latest_reasoning.md",
        llm_output
    )

    return state
