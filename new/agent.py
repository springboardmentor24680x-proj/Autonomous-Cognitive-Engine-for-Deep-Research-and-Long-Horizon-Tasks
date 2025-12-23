
# import os
# from groq import Groq
# from langsmith import traceable
# from vfs import vfs
# from todo import todo_manager

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# @traceable(name="groq_reasoning")
# def groq_reason(prompt: str) -> str:
#     res = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {"role": "system", "content": "You are a task planning autonomous agent."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3
#     )
#     return res.choices[0].message.content.strip()


# @traceable(name="agent_step")
# def agent_step(user_input, state):
#     ui = user_input.lower()

#     if ui.startswith("ls"):
#         reply = "\n".join(vfs.ls()) or "No files"

#     elif ui.startswith("read"):
#         _, name = ui.split(maxsplit=1)
#         reply = vfs.read(name)

#     elif ui.startswith("write"):
#         _, name, content = ui.split(maxsplit=2)
#         reply = vfs.write(name, content)

#     elif "todo" in ui or "plan" in ui:
#         plan = groq_reason(user_input)
#         tasks = [{"task": t, "done": False} for t in plan.split("\n") if t]
#         todo_manager.add(tasks)
#         reply = "Tasks added"

#     else:
#         reply = groq_reason(user_input)

#     state.append({"role": "assistant", "content": reply})
#     return state


#/////////////////////////////////
#//////////////////////////////////



# import os
# from groq import Groq
# from langsmith import traceable
# from vfs import vfs
# from todo import todo_manager

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# @traceable(name="groq_reasoning")
# def groq_reason(prompt: str) -> str:
#     res = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {"role": "system", "content": "You are a deep task-planning autonomous agent."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3
#     )
#     return res.choices[0].message.content.strip()


# @traceable(name="agent_step")
# def agent_step(user_input, state):
#     ui = user_input.lower()
#     reply = ""

#     # -------- VFS --------
#     if ui.startswith("ls"):
#         files = vfs.ls(state)
#         reply = "\n".join(files) if files else "📂 No files"

#     elif ui.startswith("read"):
#         _, name = ui.split(maxsplit=1)
#         reply = vfs.read(state, name)

#     elif ui.startswith("write"):
#         _, name, content = ui.split(maxsplit=2)
#         reply = vfs.write(state, name, content)

#     elif ui.startswith("edit"):
#         _, name, content = ui.split(maxsplit=2)
#         reply = vfs.edit(state, name, content)

#     # -------- TODO PLANNING --------
#     elif "todo" in ui or "plan" in ui:
#         plan = groq_reason(
#             f"Break this into clear actionable TODO tasks:\n{user_input}"
#         )
#         tasks = [
#             {"task": t.strip("- "), "done": False}
#             for t in plan.split("\n") if t.strip()
#         ]
#         todo_manager.add(state, tasks)
#         reply = "📝 Tasks added:\n" + "\n".join(f"- {t['task']}" for t in tasks)

#     # -------- DEFAULT REASONING --------
#     else:
#         reply = groq_reason(user_input)

#     state["messages"].append({"role": "assistant", "content": reply})
#     return state
import os
from groq import Groq
from langsmith import traceable
from vfs import vfs
from todo import todo_manager

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@traceable(name="groq_reasoning")
def groq_reason(prompt: str, state=None) -> str:
    memory = ""
    if state and "memory.md" in state["files"]:
        memory = f"\nLong-term memory:\n{state['files']['memory.md']}\n"

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a deep autonomous agent. "
                    "You have long-term memory stored in files. "
                    "Use relevant memory when answering.\n"
                    + memory
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return res.choices[0].message.content.strip()


def extract_and_store_memory(user_input, agent_reply, state):
    prompt = f"""
You are an autonomous agent with long-term memory.

From the interaction below, extract ONLY important information
that may be useful later (facts, goals, constraints, decisions).

Ignore casual chat.

Interaction:
User: {user_input}
Agent: {agent_reply}

Return concise bullet points.
If nothing is important, return: NONE
"""

    memory = groq_reason(prompt)

    if memory.strip().upper() != "NONE":
        existing = state["files"].get("memory.md", "")
        state["files"]["memory.md"] = (existing + "\n" + memory).strip()


@traceable(name="agent_step")
def agent_step(user_input, state):
    ui = user_input.lower()
    reply = ""

    # -------- VFS COMMANDS --------
    if ui.startswith("ls"):
        files = vfs.ls(state)
        reply = "\n".join(files) if files else " No files"

    elif ui.startswith("read"):
        _, name = ui.split(maxsplit=1)
        reply = vfs.read(state, name)

    elif ui.startswith("write"):
        _, name, content = ui.split(maxsplit=2)
        reply = vfs.write(state, name, content)

    elif ui.startswith("edit"):
        _, name, content = ui.split(maxsplit=2)
        reply = vfs.edit(state, name, content)

    # -------- TODO PLANNING --------
    elif "todo" in ui or "plan" in ui:
        plan = groq_reason(
            f"Break this into clear actionable TODO tasks:\n{user_input}",
            state,
        )
        tasks = [
            {"task": t.strip("- "), "done": False}
            for t in plan.split("\n")
            if t.strip()
        ]
        todo_manager.add(state, tasks)
        reply = " Tasks added:\n" + "\n".join(f"- {t['task']}" for t in tasks)

    # -------- DEFAULT REASONING --------
    else:
        reply = groq_reason(user_input, state)

    state["messages"].append({"role": "assistant", "content": reply})

    # 🧠 AUTO MEMORY STORAGE
    extract_and_store_memory(user_input, reply, state)

    return state
