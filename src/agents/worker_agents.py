import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Internal imports - Ensure these files exist
from src.graph.state import AgentState
from src.tools.search_tools import get_resources

# Schema for structured output
class TaskPlan(BaseModel):
    tasks: List[str] = Field(description="List of 3-5 sub-tasks")

def supervisor_node(state: AgentState):
    # Initialize the LLM (fixes "ChatGroq is not defined")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    # Terminate if already marked finished
    if state.get("is_finished"):
        return {"next_step": "end"}

    # Planning phase
    if not state.get("todo") or len(state["todo"]) == 0:
        if len(state.get("files", {})) > 0:
            return {"next_step": "end", "is_finished": True}
            
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", "Break the request into a research plan."),
            ("human", "{input}")
        ])
        
        planner = planner_prompt | llm.with_structured_output(TaskPlan)
        # We assign the result to 'plan' (fixes "plan is not defined")
        plan = planner.invoke({"input": state["input"]})
        
        return {"todo": plan.tasks, "next_step": "supervisor", "is_finished": False}

    # Delegation phase
    current_task = state["todo"][0].lower()
    if "research" in current_task:
        return {"next_step": "researcher"}
    elif "summarize" in current_task:
        return {"next_step": "summarizer"}
    
    return {"next_step": "end", "is_finished": True}

def research_agent(state: AgentState):
    task = state["todo"][0]
    content = get_resources(task)
    
    # Create a unique filename based on the number of existing files
    file_name = f"research_{len(state['files'])}.txt"
    
    return {
        "files": {**state["files"], file_name: content},
        "todo": state["todo"][1:],
        "resources": [f"Source for: {task}"]
    }

def summarizer_node(state: AgentState):
    # Logic to combine files
    combined_text = "\n".join(state["files"].values())
    return {
        "files": {**state["files"], "final_report.txt": f"Summary: {combined_text[:500]}"},
        "todo": state["todo"][1:]
    }