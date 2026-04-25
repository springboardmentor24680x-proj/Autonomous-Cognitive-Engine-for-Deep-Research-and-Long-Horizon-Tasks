from tools.todo import generate_todos
from llm.groq_llm import call_llm
from tools.search import web_search
import time

# optional sub-agents
try:
    from agents.sub_agents import research_agent, summarizer_agent
except:
    research_agent = None
    summarizer_agent = None


# 🧠 SUPERVISOR
def supervisor(state):
    print("\n👉 Supervisor running...")

    # PLAN ONLY ONCE
    if not state.get("todos"):
        print("📌 Planning tasks...")
        todos = generate_todos(state["messages"][-1]["content"])

        return {
            "todos": [{"task": t["task"], "status": "pending"} for t in todos],
            "action": "execute"
        }

    # PICK NEXT TASK
    for t in state["todos"]:
        if t["status"] == "pending":
            print("⚙️ Next task:", t["task"])
            return {
                "current_task": t["task"],
                "action": "execute"
            }

    print("🏁 All tasks completed")
    return {"action": "finish"}


# 🔧 EXECUTE TASK
def execute_task(state):
    task = state.get("current_task")

    if not task:
        return {"action": "finish"}

    print("\n🔧 Executing:", task)

    # 🧠 RULE-BASED DECISION (NO LLM CALL)
    task_lower = task.lower()

    if any(word in task_lower for word in ["research", "data", "analyze", "investigate"]):
        decision = "SEARCH"
    elif any(word in task_lower for word in ["write", "summarize", "report", "draft", "format"]):
        decision = "SUMMARIZE"
    else:
        decision = "DIRECT"

    print("🤔 Decision:", decision)

    # 🔀 ROUTING
    if decision == "SEARCH":
        print("🌐 Using Web Search")
        data = web_search(task)

        result = call_llm(f"""
Task: {task}

Use this data:
{data}

Give a detailed answer.
""")

    elif decision == "SUMMARIZE" and summarizer_agent:
        print("✍️ Using Summarizer Agent")

        files = list(state.get("files", {}).values())

        # 🔥 LIMIT INPUT SIZE (FIX 413 ERROR)
        previous_data = "\n\n".join(files[-3:])

        if len(previous_data) > 4000:
            previous_data = previous_data[:4000]

        result = summarizer_agent(previous_data)

    elif decision == "RESEARCH" and research_agent:
        print("🤖 Using Research Agent")
        result = research_agent(task)

    else:
        print("🧠 Using Direct LLM")
        result = call_llm(f"Task: {task}\nGive a detailed answer.")

    # 📁 SAVE RESULT
    files_dict = state.get("files", {})
    filename = task.replace(" ", "_")[:30] + ".txt"
    files_dict[filename] = result

    # ✅ MARK DONE
    todos = state["todos"]
    for t in todos:
        if t["task"] == task:
            t["status"] = "done"

    print("✅ Task completed")

    # 🛑 PREVENT RATE LIMIT
    time.sleep(1)

    # 🔚 CHECK COMPLETION
    if all(t["status"] == "done" for t in todos):
        return {
            "files": files_dict,
            "todos": todos,
            "action": "finish"
        }

    return {
        "files": files_dict,
        "todos": todos,
        "action": "execute"
    }


# 🧠 FINAL SYNTHESIS
def final_synthesis(state):
    print("\n🧠 Generating final report...")

    files = list(state.get("files", {}).values())

    # 🔥 LIMIT SIZE (AVOID TOKEN ERROR)
    all_data = "\n\n".join(files[-5:])

    if len(all_data) > 5000:
        all_data = all_data[:5000]

    final = call_llm(f"""
Create a structured professional report using this data:

{all_data}

Include:
- Introduction
- Key Points
- Conclusion
""")

    print("✅ Final report ready")

    return {"final_output": final}