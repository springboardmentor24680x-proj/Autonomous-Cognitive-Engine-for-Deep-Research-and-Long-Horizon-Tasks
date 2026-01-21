from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langsmith import traceable
from langchain_core.tools import tool
from src.memory.vfs import vfs  # YOUR VFS
from src.agents.supervisor_agent import supervisor_node
from src.agents.search_agent import research_node
from src.agents.summarizer_agent import summarizer_node

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    todos: Optional[list]
    langsmith_project: Optional[str]
    vfs: dict  # ADD: Your M2 VFS state

# ===== M3: DELEGATION TOOL =====
@tool
def delegate_task(agent_name: str, task: str):
    """Delegate to research/summarize agents"""
    state = {"messages": [{"content": task}]}
    if agent_name == "research":
        result = research_node(state)
    elif agent_name == "summarize":
        result = summarizer_node(state)
    vfs.write_report(f"{agent_name}_result.txt", result["messages"][-1].content)
    return f"✅ {agent_name} → {agent_name}_result.txt"

@traceable
def create_production_workflow():
    workflow = StateGraph(AgentState)
    
    # M1+M2+M3+M4 NODES
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node) 
    workflow.add_node("summarize", summarizer_node)
    workflow.add_node("tools", lambda state: {"messages": [{"role": "user", "content": "Tools executed ✅"}]})  # M4
    
    # M4: DYNAMIC ROUTING (Replace linear flow)
    workflow.add_edge(START, "supervisor")
    
    # M4: Supervisor decides next step
    def route_supervisor(state):
        todos = state.get("todos", [])
        if "research" in str(todos):
            return "research"
        elif "summarize" in str(todos):
            return "summarize" 
        elif "delegate" in str(todos):
            return "tools"
        return END
    
    workflow.add_conditional_edges("supervisor", route_supervisor)
    workflow.add_conditional_edges("tools", route_supervisor)  # Loop back
    workflow.add_edge("research", "supervisor")   # M3: Back to supervisor
    workflow.add_edge("summarize", END)
    
    return workflow.compile()

state_graph = create_production_workflow()
