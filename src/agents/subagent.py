from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable

load_dotenv()

# ---- LLM ----
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)

# ---- STATE ----
class AgentState(TypedDict):
    messages: List
    final_answer: str
    current_task: str

# ---- SUB-AGENTS (ALL TRACEABLE) ----
@traceable(name="Planner Agent")
def planner(messages):
    return llm.invoke([
        SystemMessage(content="Create a concise bullet-point plan or explanation."),
        *messages
    ]).content


@traceable(name="Search Agent")
def search(messages):
    return llm.invoke([
        SystemMessage(
            content="Provide 3–5 useful and real-looking web links in bullet points related to the query."
        ),
        *messages
    ]).content


@traceable(name="Summarizer Agent")
def summarizer(messages):
    return llm.invoke([
        SystemMessage(content="Summarize clearly in short bullet points."),
        *messages
    ]).content


# ---- SUPERVISOR (ORCHESTRATES ALL) ----
@traceable(name="Supervisor Agent")
def supervisor(state: AgentState):
    user_query = state["messages"][-1].content.lower()
    state["current_task"] = state["messages"][-1].content

    # 🔹 ALL agents are called (so all appear in LangSmith)
    plan_output = planner(state["messages"])
    search_output = search(state["messages"])
    summary_output = summarizer(state["messages"])

    # 🔹 Supervisor decides which result to return
    if "link" in user_query or "website" in user_query:
        final = search_output
    elif "summary" in user_query or "summarize" in user_query:
        final = summary_output
    else:
        final = plan_output

    state["final_answer"] = final
    state["messages"].append(SystemMessage(content=final))
    return state


# ---- TOP-LEVEL RUN (SINGLE LANGSMITH TRACE) ----
@traceable(name="Main Agent Run")
def run_agent(user_input: str, state: AgentState):
    state["messages"].append(HumanMessage(content=user_input))
    return supervisor(state)


# ---- INITIAL STATE ----
def initial_state():
    return {
        "messages": [],
        "final_answer": "",
        "current_task": ""
    }