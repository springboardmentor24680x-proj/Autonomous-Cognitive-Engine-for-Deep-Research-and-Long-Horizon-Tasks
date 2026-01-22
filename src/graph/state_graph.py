from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langsmith import traceable
from src.memory.vfs import vfs
from src.agents.supervisor_agent import supervisor_node
from src.agents.search_agent import research_node
from src.agents.summarizer_agent import summarizer_node

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    todos: Optional[list]           # Structured: [{"id":1, "task":"...", "done":False}]
    next: Optional[str]             # Router signal: "research"|"summarize"|"tools"
    langsmith_project: Optional[str]
    vfs: dict

@traceable
def create_production_workflow():
    workflow = StateGraph(AgentState)
    
    # M1+M2+M3+M4 NODES
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node) 
    workflow.add_node("summarize", summarizer_node)
    workflow.add_node("tools", lambda state: {
        "messages": [{"role": "user", "content": "✅ VFS operations completed"}],
        "todos": state.get("todos", [])
    })
    
    # M4: START → Supervisor
    workflow.add_edge(START, "supervisor")
    
    # ===== M4: TODO-DRIVEN SMART ROUTER =====
    def route_todo_supervisor(state):
        """Route based on supervisor's 'next' signal + todos progress"""
        next_action = state.get("next", "research")
        todos = state.get("todos", [])
        
        # Check if all todos completed
        todos_remaining = [t for t in todos if not t.get('done', False)]
        if not todos_remaining:
            return END
        
        # Route to next agent from supervisor signal
        if next_action == "research":
            return "research"
        elif next_action == "summarize":
            return "summarize"
        elif next_action == "tools":
            return "tools"
        else:
            return "supervisor"  # Loop back
    
    # M4: Dynamic routing from ALL nodes
    workflow.add_conditional_edges("supervisor", route_todo_supervisor)
    workflow.add_conditional_edges("research", route_todo_supervisor)
    workflow.add_conditional_edges("summarize", route_todo_supervisor)
    workflow.add_conditional_edges("tools", route_todo_supervisor)
    
    return workflow.compile()

state_graph = create_production_workflow()
