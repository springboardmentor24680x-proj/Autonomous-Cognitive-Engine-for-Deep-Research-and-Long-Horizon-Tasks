from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from typing import TypedDict

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

class SummaryState(TypedDict):
    input: str
    output: str

def summarize_node(state: SummaryState):
    result = llm.invoke(f"Briefly summarize this interaction in two sentences:\n{state['input']}")
    return {"output": result.content}

graph = StateGraph(SummaryState)
graph.add_node("summarize", summarize_node)
graph.set_entry_point("summarize")
graph.add_edge("summarize", END)
SummarizationAgent = graph.compile()