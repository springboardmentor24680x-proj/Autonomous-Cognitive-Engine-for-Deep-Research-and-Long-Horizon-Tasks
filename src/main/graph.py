import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from graph_state import AgentState

from nodes.supervisor import supervisor_node
from nodes.research import research_node
from nodes.summarize import summarize_node
from nodes.visualize import visualize_node
from nodes.calendar import calendar_node
from nodes.respond import respond_node

load_dotenv()

def build_graph():
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )

    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("supervisor", supervisor_node(llm))
    graph.add_node("research", research_node())
    graph.add_node("summarize", summarize_node())
    graph.add_node("visualize", visualize_node())
    graph.add_node("calendar", calendar_node())
    graph.add_node("respond", respond_node())

    # Entry
    graph.set_entry_point("supervisor")

    # Routing
    graph.add_conditional_edges(
        "supervisor",
        lambda s: s["intent"],
        {
            "research": "research",
            "summarize": "summarize",
            "visualize": "visualize",
            "calendar": "calendar",
            "respond": "respond"
        }
    )

    # End points
    graph.add_edge("research", "respond")
    graph.add_edge("summarize", "respond")
    graph.add_edge("visualize", "respond")
    graph.add_edge("calendar", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
