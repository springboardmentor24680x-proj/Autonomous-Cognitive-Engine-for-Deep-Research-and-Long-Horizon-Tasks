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
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to SummarizerAgent",
        metadata={
            "agent": "SummarizerAgent",
            "task_preview": task[:100],
            "has_content": bool(content),
            "content_length": len(content) if content else 0
        },
        tags=["delegation", "summarizer", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str, content_input: str = ""):
        try:
            from agents.summarizer_agent import SummarizerAgent
            
            summarizer = SummarizerAgent()
            result = summarizer.process_task(task_input, content_input)
            
            return {
                "success": True,
                "agent": "SummarizerAgent",
                "task": task_input,
                "result": result,
                "delegated_at": datetime.now().isoformat(),
                "message": f"Task successfully delegated to SummarizerAgent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "SummarizerAgent",
                "task": task_input,
                "message": f"Delegation to SummarizerAgent failed: {str(e)}"
            }
    
    return delegate_with_tracing(task, content)


@tool
def delegate_to_search_agent(task: str) -> Dict[str, Any]:
    """
    Delegate a research/search task to the specialized Search Agent.
    
    Args:
        task: Description of the research task
        
    Returns:
        Dict with delegation result and research findings
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to SearchAgent",
        metadata={
            "agent": "SearchAgent",
            "task_preview": task[:100],
            "task_type": "research"
        },
        tags=["delegation", "search", "research", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str):
        try:
            from agents.search_agent import SearchAgent
            
            search_agent = SearchAgent()
            result = search_agent.process_task(task_input)
            
            return {
                "success": True,
                "agent": "SearchAgent",
                "task": task_input,
                "result": result,
                "delegated_at": datetime.now().isoformat(),
                "message": f"Task successfully delegated to SearchAgent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "SearchAgent",
                "task": task_input,
                "message": f"Delegation to SearchAgent failed: {str(e)}"
            }
    
    return delegate_with_tracing(task)


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


@tool
def delegate_to_code_agent(task: str, code_context: str = "") -> Dict[str, Any]:
    """
    Delegate a programming task to the specialized Code Agent.
    
    Args:
        task: Description of the programming task
        code_context: Existing code context (if any)
        
    Returns:
        Dict with delegation result and code solution
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to CodeAgent",
        metadata={
            "agent": "CodeAgent",
            "task_preview": task[:100],
            "has_code_context": bool(code_context),
            "context_length": len(code_context) if code_context else 0
        },
        tags=["delegation", "code", "programming", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str, context_input: str = ""):
        try:
            from agents.code_agent import CodeAgent
            
            code_agent = CodeAgent()
            result = code_agent.process_task(task_input, context_input)
            
            return {
                "success": True,
                "agent": "CodeAgent",
                "task": task_input,
                "result": result,
                "delegated_at": datetime.now().isoformat(),
                "message": f"Task successfully delegated to CodeAgent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "CodeAgent",
                "task": task_input,
                "message": f"Delegation to CodeAgent failed: {str(e)}"
            }
    
    return delegate_with_tracing(task, code_context)


@tool
def delegate_to_planning_agent(task: str, context: str = "") -> Dict[str, Any]:
    """
    Delegate a planning task to the specialized Planning Agent.
    
    Args:
        task: Description of the planning task
        context: Additional context or requirements
        
    Returns:
        Dict with delegation result and planning solution
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to PlanningAgent",
        metadata={
            "agent": "PlanningAgent",
            "task_preview": task[:100],
            "has_context": bool(context),
            "context_length": len(context) if context else 0
        },
        tags=["delegation", "planning", "strategy", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str, context_input: str = ""):
        try:
            from agents.planning_agent import PlanningAgent
            
            planning_agent = PlanningAgent()
            result = planning_agent.process_task(task_input, context_input)
            
            # Extract the actual result content to avoid nested structure
            if result.get("success"):
                plan_content = result.get("result", result.get("plan", ""))
                return {
                    "success": True,
                    "agent": "PlanningAgent",
                    "task": task_input,
                    "result": plan_content,  # Direct content, not nested
                    "delegated_at": datetime.now().isoformat(),
                    "message": f"Task successfully delegated to PlanningAgent"
                }
            else:
                return {
                    "success": False,
                    "agent": "PlanningAgent", 
                    "task": task_input,
                    "error": result.get("error", "Unknown error"),
                    "result": f"Planning failed: {result.get('error', 'Unknown error')}",
                    "delegated_at": datetime.now().isoformat(),
                    "message": f"PlanningAgent delegation failed"
                }
            
        except Exception as e:
            return {
                "success": False,
                "agent": "PlanningAgent",
                "task": task_input,
                "error": str(e),
                "result": f"Delegation error: {str(e)}",
                "delegated_at": datetime.now().isoformat(),
                "message": f"Failed to delegate to PlanningAgent: {str(e)}"
            }
    
    return delegate_with_tracing(task, context)


@tool
def delegate_to_translation_agent(task: str, content: str = "") -> Dict[str, Any]:
    """
    Delegate a translation task to the specialized Translation Agent.
    
    Args:
        task: Description of the translation task
        content: Content to be translated
        
    Returns:
        Dict with delegation result and translation
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to TranslationAgent",
        metadata={
            "agent": "TranslationAgent",
            "task_preview": task[:100],
            "has_content": bool(content),
            "content_length": len(content) if content else 0
        },
        tags=["delegation", "translation", "localization", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str, content_input: str = ""):
        try:
            from agents.translation_agent import TranslationAgent
            
            translation_agent = TranslationAgent()
            result = translation_agent.process_task(task_input, content_input)
            
            return {
                "success": True,
                "agent": "TranslationAgent",
                "task": task_input,
                "result": result,
                "delegated_at": datetime.now().isoformat(),
                "message": f"Task successfully delegated to TranslationAgent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "TranslationAgent",
                "task": task_input,
                "message": f"Delegation to TranslationAgent failed: {str(e)}"
            }
    
    return delegate_with_tracing(task, content)


@tool
def delegate_to_creative_agent(task: str, context: str = "") -> Dict[str, Any]:
    """
    Delegate a creative content task to the specialized Creative Agent.
    
    Args:
        task: Description of the creative task
        context: Additional context or requirements for content creation
        
    Returns:
        Dict with delegation result and creative content
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Delegate to CreativeAgent",
        metadata={
            "agent": "CreativeAgent",
            "task_preview": task[:100],
            "has_context": bool(context),
            "context_length": len(context) if context else 0
        },
        tags=["delegation", "creative", "content", "sub_agent"]
    )
    def delegate_with_tracing(task_input: str, context_input: str = ""):
        try:
            from agents.creative_agent import CreativeAgent
            
            creative_agent = CreativeAgent()
            result = creative_agent.process_task(task_input, context_input)
            
            return {
                "success": True,
                "agent": "CreativeAgent",
                "task": task_input,
                "result": result,
                "delegated_at": datetime.now().isoformat(),
                "message": f"Task successfully delegated to CreativeAgent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "CreativeAgent",
                "task": task_input,
                "message": f"Delegation to CreativeAgent failed: {str(e)}"
            }
    
    return delegate_with_tracing(task, context)


@tool
def analyze_delegation_need(task: str) -> Dict[str, Any]:
    """
    Analyze a task to determine if it needs delegation and which agent to use.
    
    Args:
        task: Task description to analyze
        
    Returns:
        Dict with recommended agent, confidence, and reasoning
    """
    from langsmith import traceable
    
    @traceable(
        run_type="tool",
        name="Analyze Delegation Need",
        metadata={
            "task_preview": task[:100],
            "task_length": len(task.split()),
            "analysis_type": "delegation_need"
        },
        tags=["delegation", "analysis", "routing"]
    )
    def analyze_with_tracing(task_input: str):
        return analyze_task_for_delegation(task_input)
    
    return analyze_with_tracing(task)
def analyze_task_for_delegation(task: str) -> Dict[str, Any]:
    """
    Analyze a task to determine the best sub-agent for delegation.
    
    Args:
        task: Task description to analyze
        
    Returns:
        Dict with recommended agent and reasoning
    """
    from langsmith import traceable
    
    @traceable(
        run_type="chain",
        name="Task Delegation Analysis",
        metadata={
            "task_preview": task[:100],
            "task_length": len(task.split()),
            "analysis_type": "delegation_routing"
        },
        tags=["delegation", "analysis", "routing"]
    )
    def analyze_with_tracing(user_input: str):  # ← Parameter shows in Input tab
        task_lower = user_input.lower()
        factual_patterns = [
            "what is", "what are", "who is", "who are", "where is", "where are",
            "when is", "when are", "how many", "how much", "capital of", "population of",
            "definition of", "meaning of", "explain", "tell me about"
        ]
        
        if any(pattern in task_lower for pattern in factual_patterns):
            return {
                "recommended_agent": "SearchAgent",
                "confidence": 0.9,
                "reasoning": "Factual question best handled by research agent"
            }
        
        # Keywords for different agent types (more precise matching)
        summarization_keywords = [
            "summarize", "summary", "analyze document", "key points", "extract insights",
            "review document", "digest", "condense", "overview", "main ideas", "benefits",
            "advantages", "pros and cons", "analyze", "break down", "explain", "outline"
        ]
        
        research_keywords = [
            "research", "search for", "find information", "investigate", "explore",
            "trends", "market analysis", "news", "current events", "latest", "facts",
            "study", "examine", "look up", "discover"
        ]
        
        programming_keywords = [
            "write code", "program", "debug", "fix bug", "generate code",
            "function", "algorithm", "optimize code", "review code",
            "python function", "javascript", "java", "c++", "sql query", "api endpoint",
            "database schema", "class", "method", "variable", "write a function",
            "create a function", "code for", "script", "implement", "sort", "filter",
            "loop", "iterate", "array", "list", "dictionary", "hash", "tree", "graph"
        ]
        
        planning_keywords = [
            "plan", "strategy", "project plan", "timeline", "schedule",
            "organize", "roadmap", "milestone", "breakdown", "tasks",
            "trip plan", "business plan", "marketing strategy"
        ]
        
        translation_keywords = [
            "translate", "translation", "translate to", "localize", "localization",
            "multilingual", "spanish", "french", "german", "chinese", "japanese",
            "korean", "arabic", "hindi", "portuguese", "italian", "russian",
            "dutch", "swedish", "norwegian", "danish", "finnish", "polish",
            "czech", "hungarian", "turkish", "greek", "hebrew", "thai",
            "vietnamese", "indonesian", "malay", "filipino", "swahili",
            "convert to", "in spanish", "in french", "in german", "to english"
        ]
        
        creative_keywords = [
            "write blog", "create content", "blog post", "article", "marketing copy",
            "social media", "email template", "newsletter", "story", "creative writing",
            "brand message", "post", "campaign", "advertisement", "template", "draft",
            "brainstorm ideas", "concepts", "compose", "press release"
        ]
        
        # Use more precise matching to avoid false positives
        def count_keyword_matches(keywords, text):
            count = 0
            for keyword in keywords:
                if keyword in text:
                    # Give higher weight to exact phrase matches
                    if len(keyword.split()) > 1:
                        count += 2
                    else:
                        count += 1
            return count
        
        # Score each agent type
        summarization_score = count_keyword_matches(summarization_keywords, task_lower)
        research_score = count_keyword_matches(research_keywords, task_lower)
        programming_score = count_keyword_matches(programming_keywords, task_lower)
        planning_score = count_keyword_matches(planning_keywords, task_lower)
        creative_score = count_keyword_matches(creative_keywords, task_lower)
        translation_score = count_keyword_matches(translation_keywords, task_lower)
        
        # Find the highest scoring agent
        scores = {
            "SummarizerAgent": summarization_score,
            "SearchAgent": research_score,
            "CodeAgent": programming_score,
            "PlanningAgent": planning_score,
            "CreativeAgent": creative_score,
            "TranslationAgent": translation_score
        }
        
        max_agent = max(scores, key=scores.get)
        max_score = scores[max_agent]
        
        if max_score > 0:
            # Calculate confidence based on score
            confidence = min(max_score / 5.0, 1.0)  # Normalize confidence
            
            return {
                "recommended_agent": max_agent,
                "confidence": confidence,
                "reasoning": f"Task contains {max_score} {max_agent.replace('Agent', '').lower()}-related keywords"
            }
        else:
            # Default to SearchAgent for general questions
            return {
                "recommended_agent": "SearchAgent",
                "confidence": 0.3,
                "reasoning": "General question, defaulting to research agent"
            }
    
    return analyze_with_tracing(task)  # ← Pass task as parameter


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
        },
        {
            "name": "CodeAgent",
            "type": "programming",
            "capabilities": [
                "Code generation",
                "Bug detection and debugging",
                "Code review and analysis",
                "Performance optimization",
                "Security analysis"
            ],
            "optimal_for": [
                "Writing new code",
                "Debugging and fixing errors",
                "Code review and optimization",
                "Architecture design",
                "Security analysis"
            ]
        },
        {
            "name": "PlanningAgent",
            "type": "planning",
            "capabilities": [
                "Project planning",
                "Strategic roadmapping",
                "Task breakdown",
                "Timeline creation",
                "Resource allocation"
            ],
            "optimal_for": [
                "Project management",
                "Strategic planning",
                "Task organization",
                "Timeline scheduling",
                "Business strategy"
            ]
        },
        {
            "name": "CreativeAgent",
            "type": "creative_content",
            "capabilities": [
                "Blog posts and articles",
                "Marketing copy and sales content",
                "Social media content creation",
                "Email templates and newsletters",
                "Creative writing and storytelling",
                "Content ideation and brainstorming"
            ],
            "optimal_for": [
                "Content marketing and blogging",
                "Social media management",
                "Email marketing campaigns",
                "Creative writing projects",
                "Brand content development",
                "Marketing copy and advertisements"
            ]
        },
        {
            "name": "TranslationAgent",
            "type": "translation",
            "capabilities": [
                "Text translation between 35+ languages",
                "Document translation with formatting preservation",
                "Content localization for different cultures",
                "Multilingual content creation",
                "Translation quality assessment",
                "Cultural adaptation and context awareness"
            ],
            "optimal_for": [
                "Business document translation",
                "Website and marketing localization",
                "Technical documentation translation",
                "Multilingual content creation",
                "Cross-cultural communication",
                "Translation quality review"
            ]
        }
    ]