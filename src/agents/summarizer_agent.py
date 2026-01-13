# src/agents/summarizer_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from tools.summarize_tool import summarize_text

class SummaryState(TypedDict):
    input: str
    output: str

def summarize_node(state: SummaryState):
    summary = summarize_text.invoke(state["input"])
    return {"output": summary}

graph = StateGraph(SummaryState)
graph.add_node("summarize", summarize_node)
graph.set_entry_point("summarize")
graph.add_edge("summarize", END)

SummarizerAgent = graph.compile()
