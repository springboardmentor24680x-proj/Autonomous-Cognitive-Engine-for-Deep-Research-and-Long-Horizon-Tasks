from langsmith import traceable
from langchain_core.messages import HumanMessage, SystemMessage
from state import AgentState
from tools import planner_tool, search_tool, summarizer_tool


@traceable(name="Planner Agent")
def planner_agent(messages, active):
    return planner_tool(messages, active)


@traceable(name="Search Agent")
def search_agent(messages, active):
    return search_tool(messages, active)


@traceable(name="Summarizer Agent")
def summarizer_agent(messages, active):
    return summarizer_tool(messages, active)


@traceable(name="Supervisor Agent")
def supervisor(state: AgentState) -> AgentState:
    messages = state["messages"]
    user_input = messages[-1].content
    state["current_task"] = user_input

    # ---- intent routing ----
    is_search = any(k in user_input.lower() for k in ["link", "website", "site"])
    is_summary = any(k in user_input.lower() for k in ["summary", "summarize"])
    is_plan = not (is_search or is_summary)

    # ---- ALL agents run (continuous + visible) ----
    plan_out = planner_agent(messages, is_plan)
    search_out = search_agent(messages, is_search)
    summary_out = summarizer_agent(messages, is_summary)

    if is_search:
        final = search_out
    elif is_summary:
        final = summary_out
    else:
        final = plan_out

    for agent, tool, output, active in [
        ("Planner", "Planner Tool", plan_out, is_plan),
        ("Search", "Search Tool", search_out, is_search),
        ("Summarizer", "Summarizer Tool", summary_out, is_summary),
    ]:
        state["todo_status"].append({
            "task": user_input,
            "agent": agent,
            "tool": tool,
            "status": "Used" if active else "Skipped",
            "output": output[:300]
        })

    state["final_answer"] = final
    state["messages"].append(SystemMessage(content=final))
    return state


@traceable(name="Main Agent Run")
def run_agent(user_input: str, state: AgentState) -> AgentState:
    state["messages"].append(HumanMessage(content=user_input))
    return supervisor(state)


def initial_state() -> AgentState:
    return {
        "messages": [],
        "final_answer": "",
        "current_task": "",
        "todo_status": []
    }