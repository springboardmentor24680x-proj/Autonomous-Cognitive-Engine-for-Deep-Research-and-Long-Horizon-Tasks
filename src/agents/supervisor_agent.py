from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from memory.vfs import append_memory, load_memory

# -------------------------------
# LLM
# -------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


# -------------------------------
# State
# -------------------------------
class SupervisorState(TypedDict):
    input: str
    plan: str
    search_result: str
    response: str
    output: str

# -------------------------------
# Utilities
# -------------------------------
def is_greeting(text: str) -> bool:
    greetings = {
        "hi", "hello", "hey",
        "good morning", "good afternoon", "good evening",
        "how are you", "what's up","bye","Thank You"
    }
    text = text.lower().strip()
    return any(text == g or text.startswith(g + " ") for g in greetings)


# -------------------------------
# Nodes
# -------------------------------
def planner_node(state: SupervisorState):
    #  HIDDEN SHORT-CIRCUIT FOR GREETINGS
    if is_greeting(state["input"]):
        res = llm.invoke(state["input"])

        append_memory("user", state["input"])
        append_memory("assistant", res.content)

        return {
            "output": res.content,
            "plan": "__DIRECT__"  # internal marker
        }

    # NORMAL PLANNING
    res = llm.invoke(f"Create a short TODO plan to answer:\n{state['input']}")
    
    return {"plan": res.content}


def search_node(state: SupervisorState):
    result = SearchAgent.invoke({
        "query": state["input"]
    })
    return {"search_result": result["result"]}


def respond_node(state: SupervisorState):
    memory = load_memory()
    context = "\n".join(
        [f"{m['role']}: {m['content']}" for m in memory[-5:]]
    )

    prompt = f"""
You are a helpful AI.

Conversation Context:
{context}

Plan:
{state['plan']}

Search Info:
{state['search_result']}

User:
{state['input']}

Assistant:
"""

    res = llm.invoke(prompt)

    append_memory("user", state["input"])
    append_memory("assistant", res.content)

    return {"response": res.content}


def summarize_node(state: SupervisorState):
    summary = SummarizerAgent.invoke({
        "input": f"User: {state['input']}\nAI: {state['response']}"
    })["output"]

    append_memory("summary", summary)

    return {
        "output": f"{state['response']}\n\n---\n### Summary\n{summary}"
    }


# -------------------------------
# Graph
# -------------------------------
graph = StateGraph(SupervisorState)

graph.add_node("planner", planner_node)
graph.add_node("search", search_node)
graph.add_node("respond", respond_node)
graph.add_node("summarize", summarize_node)

graph.set_entry_point("planner")

#  GREETING SHORT-CIRCUIT (HIDDEN)
graph.add_conditional_edges(
    "planner",
    lambda state: "__DIRECT__" if state["plan"] == "__DIRECT__" else "SEARCH",
    {
        "__DIRECT__": END,
        "SEARCH": "search",
    }
)


#  NORMAL FLOW
graph.add_edge("search", "respond")
graph.add_edge("respond", "summarize")
graph.add_edge("summarize", END)

SupervisorAgent = graph.compile()
