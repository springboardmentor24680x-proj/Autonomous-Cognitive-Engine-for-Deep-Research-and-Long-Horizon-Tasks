from typing import Annotated, TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

# Modular Imports
from src.agents.supervisor_agent import call_research_agent
from src.tools.write_file import write_file
from src.tools.read_file import read_file
from src.tools.write_todos import write_todos
from src.memory.vfs import VFSManager

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    vfs: Dict[str, str]
    todos: List[str]

def supervisor_node(state: AgentState):
    """
    Main Supervisor (The Brain).
    Uses 70B for high-quality logic, but with trimmed history.
    """
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    tools = [call_research_agent, write_file, read_file, write_todos]
    agent = llm.bind_tools(tools)
    
    system_msg = SystemMessage(content=(
        "You are the Supervisor. Be brief. \n"
        "1. Plan with 'write_todos'.\n"
        "2. Research with 'call_research_agent'.\n"
        "3. Save with 'write_file'.\n"
        "Finish once tasks are complete."
    ))
    
    # RECTIFICATION: Clean and Trim history to solve 400 and 429 errors
    clean_history = []
    # Only look at the last 6 messages to keep tokens low
    for m in state["messages"][-6:]:
        # Skip internal XML function tags that cause the 400 error
        if isinstance(m.content, str) and "<function" not in m.content:
            clean_history.append(m)
        elif not isinstance(m.content, str):
            clean_history.append(m)

    response = agent.invoke([system_msg] + clean_history)
    return {"messages": [response]}

def create_graph():
    tools = [call_research_agent, write_file, read_file, write_todos]
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("action", ToolNode(tools))
    workflow.add_node("update", VFSManager.process_tool_calls)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor", 
        lambda x: "action" if x["messages"][-1].tool_calls else END
    )
    workflow.add_edge("action", "update")
    workflow.add_edge("update", "supervisor")
    
    return workflow.compile()