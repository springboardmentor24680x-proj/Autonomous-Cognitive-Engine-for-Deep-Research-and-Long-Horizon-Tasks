from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from src.tools.search_tool import search_tool

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]

def research_node(state: ResearchState):
    """
    Sub-agent for web research. 
    Uses Llama-3.1-8b to save your 70B token quota.
    """
    # Optimized for speed and rate-limit safety
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    agent = llm.bind_tools([search_tool])
    
    # We only send the last few messages to the sub-agent to stay under limits
    context = state["messages"][-5:]
    return {"messages": [agent.invoke(context)]}

workflow = StateGraph(ResearchState)
workflow.add_node("researcher", research_node)
workflow.add_node("tools", ToolNode([search_tool]))

workflow.add_edge(START, "researcher")
workflow.add_conditional_edges(
    "researcher", 
    lambda x: "tools" if x["messages"][-1].tool_calls else END
)
workflow.add_edge("tools", "researcher")

search_agent = workflow.compile()