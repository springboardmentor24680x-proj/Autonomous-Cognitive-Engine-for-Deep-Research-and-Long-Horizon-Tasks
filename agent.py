

# import os
# from groq import Groq
# from vfs import vfs
# from todo import todo_manager

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# def groq_reason(prompt):
#     try:
#         res = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": "You are a task planning autonomous agent."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3
#         )
#         result = res.choices[0].message.content.strip()
#         return result
#     except Exception as e:
#         return f"Error: {e}"


# def agent_step(user_input, state):
#     ui = user_input.lower()

#     # ---------------- VFS ----------------
#     if ui.startswith("ls"):
#         reply = "\n".join(vfs.ls()) or "No files"

#     elif ui.startswith("read"):
#         parts = ui.split(maxsplit=1)
#         if len(parts) < 2:
#             reply = "Usage: read <filename>"
#         else:
#             reply = vfs.read(parts[1])

#     elif ui.startswith("write"):
#         parts = ui.split(maxsplit=2)
#         if len(parts) < 3:
#             reply = "Usage: write <filename> <content>"
#         else:
#             reply = vfs.write(parts[1], parts[2])

#     elif ui.startswith("edit"):
#         parts = ui.split(maxsplit=2)
#         if len(parts) < 3:
#             reply = "Usage: edit <filename> <content>"
#         else:
#             reply = vfs.edit(parts[1], parts[2])

#     # ---------------- TODO ----------------
#     elif "todo" in ui or "plan" in ui:
#         plan = groq_reason(f"Split this into actionable TODO tasks:\n{user_input}")

#         tasks = [
#             {"task": t.strip("- "), "done": False}
#             for t in plan.split("\n") if t.strip()
#         ]

#         todo_manager.add(tasks)
#         reply = "Tasks added:\n" + "\n".join(f"- {t['task']}" for t in tasks)

#     elif ui == "todos":
#         todos = todo_manager.list()
#         reply = "\n".join(
#             f"{i}. {'✅' if t['done'] else '⬜'} {t['task']}" for i, t in enumerate(todos)
#         ) or "No todos"

#     # ---------------- DEFAULT ----------------
#     else:
#         reply = groq_reason(user_input)

#     state.append({"role": "assistant", "content": reply})
#     return state
import os
from groq import Groq
from langsmith import traceable
from vfs import vfs
from todo import todo_manager

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@traceable(name="groq_reasoning")
def groq_reason(prompt: str) -> str:
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a task planning autonomous agent."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return res.choices[0].message.content.strip()


@traceable(name="agent_step")
def agent_step(user_input, state):
    ui = user_input.lower()

    if ui.startswith("ls"):
        reply = "\n".join(vfs.ls()) or "No files"

    elif ui.startswith("read"):
        _, name = ui.split(maxsplit=1)
        reply = vfs.read(name)

    elif ui.startswith("write"):
        _, name, content = ui.split(maxsplit=2)
        reply = vfs.write(name, content)

    elif "todo" in ui or "plan" in ui:
        plan = groq_reason(user_input)
        tasks = [{"task": t, "done": False} for t in plan.split("\n") if t]
        todo_manager.add(tasks)
        reply = "Tasks added"

    else:
        reply = groq_reason(user_input)

    state.append({"role": "assistant", "content": reply})
    return state
