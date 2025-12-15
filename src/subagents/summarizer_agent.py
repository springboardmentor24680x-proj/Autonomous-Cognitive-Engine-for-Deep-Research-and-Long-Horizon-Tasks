from typing import TypedDict
from langgraph.graph import StateGraph
import groq
import os

class SummarizerState(TypedDict):
    input: str
    output: str

def summarize(state: SummarizerState):
    client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional summarization agent."},
            {"role": "user", "content": state["input"]}
        ],
        max_tokens=600
    )

    state["output"] = response.choices[0].message.content
    return state

graph = StateGraph(SummarizerState)
graph.add_node("summarize", summarize)
graph.add_edge("__start__", "summarize")
graph.add_edge("summarize", "__end__")

summarizer_agent = graph.compile()
