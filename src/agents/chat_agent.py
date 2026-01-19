import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable, get_current_run_tree

from tools.vfs_tools import (
    ensure_files, ls, read, write, edit, delete, clear, rename, help_text
)
from utils.llm import call_llm, clean_text
from agents.delegation_tool import delegate_task

# ================= CONFIG =================

MAX_MEMORY_TURNS = 4
PLANS_FILE = "plans.json"
CALENDAR_FILE = "calendar.json"

# ================= SESSION =================

def ensure_conversation_id(state):
    if "conversation_id" not in state:
        state["conversation_id"] = str(uuid.uuid4())

# ================= CHAT MEMORY =================

def ensure_memory(state):
    state.setdefault("chat_history", [])

def add_to_memory(state, role, content):
    state["chat_history"].append({
        "role": role,
        "content": content,
        "time": datetime.utcnow().isoformat()
    })
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

# ================= INTERNAL AUTO PLANNING =================

def ensure_plans(state):
    state.setdefault("files", {})
    if PLANS_FILE not in state["files"]:
        state["files"][PLANS_FILE] = json.dumps({"plans": []}, indent=2)

@traceable(name="Auto Task Planning")
def auto_todo_plan(state, task: str):
    """
    Internal planning ONLY (never shown to user)
    """
    ensure_plans(state)

    prompt = f"""
Break the following task into 3–5 short actionable steps.

Task:
{task}
"""
    raw = call_llm(prompt)

    steps = [
        l.strip("-•0123456789. ").strip()
        for l in raw.splitlines()
        if len(l.split()) >= 2
    ]

    data = json.loads(state["files"][PLANS_FILE])
    data["plans"].append({
        "task": task,
        "steps": steps,
        "created": datetime.utcnow().isoformat()
    })
    state["files"][PLANS_FILE] = json.dumps(data, indent=2)

    return steps

@traceable(name="Plan Requirement Check")
def requires_plan(text: str, agents: list) -> bool:
    if len(agents) > 1:
        return True
    if len(text.split()) > 15:
        return True
    return False

# ================= CALENDAR =================

def ensure_calendar(state):
    state.setdefault("files", {})
    if CALENDAR_FILE not in state["files"]:
        state["files"][CALENDAR_FILE] = json.dumps({"events": []}, indent=2)

@traceable(
    name="Calendar Add",
      run_type="tool" ,
    tags=["calendar", "tool"]
    
)
def add_calendar_event(state, title, when):
    ensure_calendar(state)

    data = json.loads(state["files"][CALENDAR_FILE])
    data["events"].append({
        "title": title,
        "time": when,
        "created": datetime.utcnow().isoformat()
    })

    state["files"][CALENDAR_FILE] = json.dumps(data, indent=2)
    return f"📅 Event added: {title} → {when}"

# ================= MULTI-AGENT DECISION =================

@traceable(name="Delegation Decision")
def should_delegate(text: str):
    low = text.lower()
    agents = []

    if any(k in low for k in ["search", "find", "lookup"]):
        agents.append("web_search")

    if any(k in low for k in ["code", "python", "java", "debug", "error"]):
        agents.append("code")

    if "summarize" in low or "summary" in low:
        agents.append("summarize")

    return agents

@traceable(name="ChatSession", tags=["chat", "main-session"])
def handle_message(state: dict, user_text: str):
    # ---------- SESSION SETUP ----------
    ensure_conversation_id(state)
    ensure_files(state)
    ensure_memory(state)
    ensure_plans(state)
    ensure_calendar(state)

    # 🔗 Attach LangSmith metadata
    run = get_current_run_tree()
    if run:
        run.metadata["conversation_id"] = state["conversation_id"]
        run.metadata["turn"] = len(state["chat_history"]) // 2 + 1
        run.metadata["input"] = user_text

    text = user_text.strip()

    # ---------- HELP ----------
    if text.lower() in ("help", "vfs.help"):
        return state, help_text()

    # ---------- VFS COMMANDS ----------
    if text == "ls":
        return state, "\n".join(ls(state))

    if text.startswith("read "):
        return state, read(state, text.split(" ", 1)[1])

    if text.startswith("write "):
        _, f, c = text.split(" ", 2)
        return state, write(state, f, c)

    if text.startswith("edit! "):
        _, f, c = text.split(" ", 2)
        return state, edit(state, f, c, mode="overwrite")

    if text.startswith("edit "):
        _, f, c = text.split(" ", 2)
        return state, edit(state, f, c)

    if text.startswith("delete "):
        return state, delete(state, text.split(" ", 1)[1])

    if text.startswith("clear "):
        return state, clear(state, text.split(" ", 1)[1])

    if text.startswith("rename "):
        _, o, n = text.split(" ", 2)
        return state, rename(state, o, n)

    # ---------- CALENDAR COMMAND ----------
    # Example: calendar.add Birthday 2026-09-01
    if text.lower().startswith("calendar.add"):
        try:
            _, title, date = text.split(" ", 2)
            reply = add_calendar_event(state, title, date)
            add_to_memory(state, "assistant", reply)
            return state, reply
        except:
            reply = " Usage: calendar.add <title> <YYYY-MM-DD>"
            add_to_memory(state, "assistant", reply)
            return state, reply

    # ---------- NORMAL CHAT ----------
    add_to_memory(state, "user", user_text)

    #  Decide sub-agents
    agents = should_delegate(user_text)

    #  INTERNAL AUTO PLANNING (TRACING ONLY, NOT SHOWN IN UI)
    if requires_plan(user_text, agents):
        auto_todo_plan(state, user_text)

    # 🤝 SUB-AGENT EXECUTION
    outputs = []
    for agent in agents:
        result = delegate_task(agent, user_text)
        outputs.append(f"🤝 **{agent} agent:**\n{result}")

    # SUPERVISOR LLM IF NO AGENT
    if outputs:
        reply = "\n\n".join(outputs)
    else:
        prompt = build_llm_prompt(state, user_text)
        raw = call_llm(prompt)
        reply = clean_text(raw)

    # ---------- SAVE MEMORY ----------
    add_to_memory(state, "assistant", reply)

    return state, reply
