import os
from typing import TypedDict
from langgraph.graph import StateGraph
from langsmith import traceable
import groq
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY")

client = groq.Client(api_key=GROQ_API_KEY)

# ---------------- STATE ----------------
class SummarizerState(TypedDict):
    text: str
    summary: str

# ---------------- LLM ----------------
@traceable(name="Summarizer_LLM", run_type="llm")
def summarize_text(text: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional text summarizer."},
            {"role": "user", "content": f"Summarize the following clearly:\n\n{text}"}
        ],
        max_tokens=500
    )
    return resp.choices[0].message.content.strip()

# ---------------- NODE ----------------
@traceable(name="Summarizer_Node", run_type="chain")
def summarizer_node(state: SummarizerState) -> SummarizerState:
    summary = summarize_text(state["text"])
    state["summary"] = summary
    return state

# ---------------- GRAPH ----------------
graph = StateGraph(SummarizerState)
graph.add_node("summarize", summarizer_node)
graph.add_edge("__start__", "summarize")
graph.add_edge("summarize", "__end__")

summarizer_app = graph.compile()
