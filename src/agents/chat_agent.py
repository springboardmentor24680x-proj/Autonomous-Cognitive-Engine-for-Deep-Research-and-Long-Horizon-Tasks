
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from tools.vfs_tools import (
    ensure_files, ls, read, write, edit, delete, clear, rename, help_text
)
from utils.llm import call_llm, clean_text
from agents.delegation_tool import delegate_task

# ================= CONFIG =================
MAX_MEMORY_TURNS = 4
TODOS_FILE = "todos.json"
CALENDAR_FILE = "calendar.json"

# ================= CHAT MEMORY =================

def ensure_memory(state):
    state.setdefault("chat_history", [])

def add_to_memory(state, role, content):
    state["chat_history"].append({"role": role, "content": content})
    state["chat_history"] = state["chat_history"][-MAX_MEMORY_TURNS * 2:]

def build_llm_prompt(state, user_text):
    recent = state["chat_history"][-4:]
    lines = []
    for msg in recent:
        prefix = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {msg['content']}")
    lines.append(f"User: {user_text}")
    lines.append("Assistant:")
    return "\n".join(lines)

# ================= VFS JSON HELPERS =================

def ensure_json_file(state, filename, default):
    state.setdefault("files", {})
    if filename not in state["files"]:
        state["files"][filename] = json.dumps(default, indent=2)

def read_json(state, filename):
    return json.loads(state["files"][filename])

def write_json(state, filename, data):
    state["files"][filename] = json.dumps(data, indent=2)

# ================= TODO =================

def ensure_todos(state):
    ensure_json_file(state, TODOS_FILE, {"todos": []})

def clean_steps(raw_text, max_steps):
    steps = []
    for line in raw_text.splitlines():
        line = line.strip().lstrip("-•0123456789. ").strip()
        if line and 2 <= len(line.split()) <= 10:
            steps.append(line)
    return steps[:max_steps]

def todo_plan(state, task, n_steps=10):
    ensure_todos(state)

    prompt = f"""
Create {n_steps} TODO steps for the following task.
Rules:
- No numbering

Task: {task}
"""
    raw = call_llm(prompt)
    steps = clean_steps(raw, n_steps)

    if not steps:
        steps = [f"Work on: {task} (step {i+1})" for i in range(n_steps)]

    data = read_json(state, TODOS_FILE)
    data["todos"].append({
        "task": task,
        "steps": steps,
        "created": datetime.utcnow().isoformat()
    })
    write_json(state, TODOS_FILE, data)

    return (
        " **TODO plan created successfully.**\n\n"
        + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    )

def list_todos(state):
    ensure_todos(state)
    return state["files"][TODOS_FILE]

# ================= CALENDAR =================

def ensure_calendar(state):
    ensure_json_file(state, CALENDAR_FILE, {"events": []})

def add_calendar_event(state, title, when):
    ensure_calendar(state)

    data = read_json(state, CALENDAR_FILE)
    data["events"].append({
        "title": title,
        "time": when,
        "created": datetime.utcnow().isoformat()
    })
    write_json(state, CALENDAR_FILE, data)

    return f" **Event added:** {title} → {when}"

def list_calendar_events(state):
    ensure_calendar(state)
    data = read_json(state, CALENDAR_FILE)

    if not data["events"]:
        return " No calendar events saved yet."

    return "\n".join(
        f"{i+1}. {e['title']} → {e['time']}"
        for i, e in enumerate(data["events"])
    )

# ================= DELEGATION DECISION =================

def should_delegate(text: str):
    """
    Decide whether the task should be delegated
    to a specialized sub-agent.
    """
    low = text.lower()

    # Summarization intent
    if low.startswith("summarize"):
        return "summarize"

    # Web search intent
    if low.startswith("search") or low.startswith("web search"):
        return "web_search"

    return None

# ================= MAIN HANDLER =================

def handle_message(state: dict, user_text: str):
    ensure_files(state)
    ensure_memory(state)
    ensure_todos(state)
    ensure_calendar(state)

    text = user_text.strip()
    low = text.lower()

    # -------- HELP --------
    if low in ("help", "vfs.help"):
        return state, help_text()

    # -------- VFS --------
    if low == "ls":
        files = ls(state)
        return state, ("\n".join(files) if files else "No files available.")

    if low.startswith("read "):
        return state, read(state, text.split(" ", 1)[1])

    if low.startswith("write "):
        parts = text.split(" ", 2)
        return state, write(state, parts[1], parts[2])

    if low.startswith("edit! "):
        parts = text.split(" ", 2)
        return state, edit(state, parts[1], parts[2], mode="overwrite")

    if low.startswith("edit "):
        parts = text.split(" ", 2)
        return state, edit(state, parts[1], parts[2])

    if low.startswith("delete "):
        return state, delete(state, text.split(" ", 1)[1])

    if low.startswith("clear "):
        return state, clear(state, text.split(" ", 1)[1])

    if low.startswith("rename "):
        parts = text.split(" ", 2)
        return state, rename(state, parts[1], parts[2])

    # -------- TODO --------
    if low.startswith("todo.plan"):
        task = text[len("todo.plan"):].strip()
        return state, todo_plan(state, task)

    if low == "todo.list":
        return state, list_todos(state)

    # -------- CALENDAR --------
    if low.startswith("calendar.add"):
        title, when = map(str.strip, text[len("calendar.add"):].split("|", 1))
        return state, add_calendar_event(state, title, when)

    if low == "calendar.list":
        return state, list_calendar_events(state)

    # -------- CHAT + SUB-AGENT DELEGATION --------
    add_to_memory(state, "user", text)

    delegation_type = should_delegate(text)

    if delegation_type:
        result = delegate_task(delegation_type, text)
        reply = f" **Delegated to {delegation_type} agent:**\n\n{result}"
    else:
        prompt = build_llm_prompt(state, text)
        reply = clean_text(call_llm(prompt))

    add_to_memory(state, "assistant", reply)
    return state, reply
