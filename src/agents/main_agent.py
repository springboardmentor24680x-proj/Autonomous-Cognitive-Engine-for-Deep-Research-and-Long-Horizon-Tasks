import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from agents.summarization_agent import SummarizationAgent
from agents.planner_agent import PlannerAgent
from agents.search_agent import WebSearchAgent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

class GlobalState(TypedDict):
    input: str
    history: Annotated[List[str], operator.add]
    search_result: str
    plan: str
    response: str
    summary: str
    output: str

# --- Delegation Nodes ---
def call_search(state: GlobalState):
    res = WebSearchAgent.invoke({"query": state["input"]})
    return {"search_result": res.get("result", "")}

def call_planner(state: GlobalState):
    res = PlannerAgent.invoke({"input": state["input"], "history": state["history"]})
    return {"plan": res.get("plan", "")}

def response_node(state: GlobalState):
    # This node synthesizes all sub-agent data into a human response
    prompt = f"""
    System: You are a friendly AI. Use the context/plan provided to answer naturally.
    Never mention internal technical terms like 'Node' or 'State'.
    Context: {state.get('search_result', '')}
    Plan: {state.get('plan', '')}
    User: {state['input']}
    Assistant:"""
    res = llm.invoke(prompt)
    return {"response": res.content}

def summarize_node(state: GlobalState):
    # Only summarize the current turn
    text_to_sum = f"User: {state['input']}\nAI: {state['response']}"
    res = SummarizationAgent.invoke({"input": text_to_sum})
    
    # Format the final output for the Streamlit UI
    final_output = f"{state['response']}\n\n---\n### 📝 Summary\n{res.get('output', '')}"
    return {"summary": res.get('output', ''), "output": final_output}

# --- Smart Router ---
def router(state: GlobalState):
    # Ask the LLM where to go (Delegation)
    prompt = f"Categorize this user intent as SEARCH, PLANNER, or RESPOND: {state['input']}"
    category = llm.invoke(prompt).content.upper()
    
    if "SEARCH" in category: return "search_agent"
    if "PLANNER" in category: return "planner_agent"
    return "respond"

# --- Graph Assembly ---
workflow = StateGraph(GlobalState)
workflow.add_node("search_agent", call_search)
workflow.add_node("planner_agent", call_planner)
workflow.add_node("respond", response_node)
workflow.add_node("summarize", summarize_node)

workflow.set_conditional_entry_point(router, {
    "search_agent": "search_agent",
    "planner_agent": "planner_agent",
    "respond": "respond"
})

workflow.add_edge("search_agent", "respond")
workflow.add_edge("planner_agent", "respond")
workflow.add_edge("respond", "summarize")
workflow.add_edge("summarize", END)

MainAgent = workflow.compile()