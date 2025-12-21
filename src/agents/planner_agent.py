from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

class PlannerState(TypedDict):
    input: str
    history: List[str]
    plan: str

def planner_node(state: PlannerState):
    prompt = f"Create a step-by-step TODO plan for: {state['input']}. Keep it actionable."
    result = llm.invoke(prompt)
    return {"plan": result.content}

graph = StateGraph(PlannerState)
graph.add_node("planner", planner_node)
graph.set_entry_point("planner")
graph.add_edge("planner", END)
PlannerAgent = graph.compile()