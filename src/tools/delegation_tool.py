#!/usr/bin/env python3
"""
Task Delegation Tool - Enables the supervisor to delegate tasks to specialized sub-agents
Part of Milestone 3: Sub-Agent Delegation
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
from datetime import datetime


@tool
def delegate_to_summarizer(task: str, content: str = "") -> Dict[str, Any]:
    """
    Delegate a summarization task to the specialized Summarizer Agent.
    
    Args:
        task: Description of the summarization task
        content: Content to be summarized (if available)
        
    Returns:
        Dict with delegation result and summary
    """
    try:
        from agents.summarizer_agent import SummarizerAgent
        
        summarizer = SummarizerAgent()
        result = summarizer.process_task(task, content)
        
        return {
            "success": True,
            "agent": "SummarizerAgent",
            "task": task,
            "result": result,
            "delegated_at": datetime.now().isoformat(),
            "message": f"Task successfully delegated to SummarizerAgent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "SummarizerAgent",
            "task": task,
            "message": f"Delegation to SummarizerAgent failed: {str(e)}"
        }


@tool
def delegate_to_search_agent(task: str) -> Dict[str, Any]:
    """
    Delegate a research/search task to the specialized Search Agent.
    
    Args:
        task: Description of the research task
        
    Returns:
        Dict with delegation result and research findings
    """
    try:
        from agents.search_agent import SearchAgent
        
        search_agent = SearchAgent()
        result = search_agent.process_task(task)
        
        return {
            "success": True,
            "agent": "SearchAgent",
            "task": task,
            "result": result,
            "delegated_at": datetime.now().isoformat(),
            "message": f"Task successfully delegated to SearchAgent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "SearchAgent",
            "task": task,
            "message": f"Delegation to SearchAgent failed: {str(e)}"
        }


@tool
def create_todo_item(task: str, priority: str = "medium") -> Dict[str, Any]:
    """
    Create a new TODO item for task tracking.
    
    Args:
        task: Description of the task
        priority: Priority level (low, medium, high)
        
    Returns:
        Dict with TODO item details
    """
    try:
        from memory.vfs import get_current_agent_state, update_agent_state
        
        # Generate unique ID
        todo_id = f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        todo_item = {
            "id": todo_id,
            "task": task,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_agent": None
        }
        
        # Add to agent state
        state = get_current_agent_state()
        if "todos" not in state:
            state["todos"] = []
        
        state["todos"].append(todo_item)
        update_agent_state("todos", "todos", state["todos"])
        
        return {
            "success": True,
            "todo_id": todo_id,
            "todo_item": todo_item,
            "message": f"TODO item created: {task}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create TODO item: {str(e)}"
        }


def get_available_agents() -> List[Dict[str, Any]]:
    """
    Get list of available sub-agents for delegation.
    
    Returns:
        List of available agents with their capabilities
    """
    return [
        {
            "name": "SummarizerAgent",
            "type": "summarization",
            "capabilities": [
                "Text summarization",
                "Document analysis", 
                "Key point extraction",
                "Content structure analysis"
            ],
            "optimal_for": [
                "Long document summarization",
                "Research paper analysis",
                "Meeting notes processing",
                "Content review and synthesis"
            ]
        },
        {
            "name": "SearchAgent",
            "type": "research",
            "capabilities": [
                "Web research",
                "Information gathering",
                "Fact checking",
                "Trend analysis",
                "Market research"
            ],
            "optimal_for": [
                "Current information gathering",
                "Market analysis",
                "Competitive research",
                "News and events research"
            ]
        }
    ]


def analyze_task_for_delegation(task: str) -> Dict[str, Any]:
    """
    Analyze a task to determine the best sub-agent for delegation.
    
    Args:
        task: Task description to analyze
        
    Returns:
        Dict with recommended agent and reasoning
    """
    task_lower = task.lower()
    
    # Keywords for different agent types
    summarization_keywords = [
        "summarize", "summary", "analyze", "key points", "extract",
        "review", "digest", "condense", "overview", "main ideas"
    ]
    
    research_keywords = [
        "research", "search", "find", "investigate", "explore",
        "trends", "market", "news", "current", "latest", "facts"
    ]
    
    # Score each agent type
    summarization_score = sum(1 for keyword in summarization_keywords if keyword in task_lower)
    research_score = sum(1 for keyword in research_keywords if keyword in task_lower)
    
    if summarization_score > research_score:
        return {
            "recommended_agent": "SummarizerAgent",
            "confidence": min(summarization_score / len(summarization_keywords), 1.0),
            "reasoning": f"Task contains {summarization_score} summarization-related keywords"
        }
    elif research_score > summarization_score:
        return {
            "recommended_agent": "SearchAgent", 
            "confidence": min(research_score / len(research_keywords), 1.0),
            "reasoning": f"Task contains {research_score} research-related keywords"
        }
    else:
        return {
            "recommended_agent": None,
            "confidence": 0.0,
            "reasoning": "Task doesn't clearly match any specialized agent"
        }