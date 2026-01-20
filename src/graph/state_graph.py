from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langsmith import traceable
from src.agents.supervisor_agent import supervisor_node
from src.agents.search_agent import research_node
from src.agents.summarizer_agent import summarizer_node

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    todos: Optional[list]
    langsmith_project: Optional[str]

@traceable
def create_production_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node) 
    workflow.add_node("summarize", summarizer_node)
    
    # Linear production flow
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("supervisor", "research")
    workflow.add_edge("research", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()

state_graph = create_production_workflow()
