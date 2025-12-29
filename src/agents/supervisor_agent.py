#!/usr/bin/env python3
"""
Supervisor Agent - Main orchestrator for multi-agent workflow automation
Coordinates task planning, sub-agent delegation, and memory management
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Import tools from the tools module
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls
from tools.search_tool import web_search
from tools.delegation_tool import (
    delegate_to_summarizer, 
    delegate_to_search_agent, 
    create_todo_item,
    analyze_task_for_delegation,
    get_available_agents
)
from memory.vfs import get_current_agent_state, update_agent_state, get_vfs


class SupervisorAgent:
    """
    Main supervisor agent that orchestrates the entire workflow.
    Handles task analysis, planning, execution coordination, and synthesis.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the supervisor agent with LLM and tools."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,
            max_tokens=1200
        )
        
        self.model = model_name
        
        # Initialize agent state
        self._initialize_state()
        
        # Create the chain
        self.chain = self._create_chain()
    
    def _initialize_state(self):
        """Initialize the global agent state."""
        global _current_agent_state
        _current_agent_state = {
            "virtual_files": {},
            "todos": [],
            "current_todo_id": None,
            "step_count": 0,
            "max_steps": 10
        }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are a helpful AI assistant. Be practical, direct, and actually helpful.

{current_info}

CORE PRINCIPLES:
- PROVIDE ACTUAL HELP: Don't just ask more questions - give useful, actionable advice
- BE DIRECT: Get to the point quickly and provide concrete solutions
- ASSUME REASONABLE DEFAULTS: If details are missing, make reasonable assumptions and provide helpful suggestions
- GIVE EXAMPLES: Provide specific examples, templates, or step-by-step guidance
- BE COMPLETE: Give comprehensive answers that actually solve the user's problem

RESPONSE APPROACH:
- For invitations: Provide actual invitation text/templates
- For planning: Give specific plans with details
- For questions: Give direct, complete answers
- For requests: Provide actionable solutions immediately

AVOID:
- Asking too many follow-up questions
- Being vague or unhelpful
- Repeating the same information
- Over-analyzing simple requests

Be like a knowledgeable friend who actually helps solve problems instead of just talking about them."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def analyze_task(self, user_input: str) -> Dict[str, Any]:
        """Analyze the user input to determine task complexity and requirements."""
        analysis_prompt = f"""
        Analyze this user request and determine:
        1. Task complexity (simple/moderate/complex)
        2. Required capabilities (research, analysis, planning, etc.)
        3. Whether sub-agent delegation would be beneficial
        4. Memory/context requirements
        
        User request: {user_input}
        
        Provide a brief analysis in JSON format.
        """
        
        try:
            analysis = self.llm.invoke(analysis_prompt)
            return {
                "success": True,
                "analysis": analysis,
                "complexity": "moderate",  # Default fallback
                "requires_delegation": False,
                "requires_memory": False
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "complexity": "simple",
                "requires_delegation": False,
                "requires_memory": False
            }
    
    def plan_execution(self, user_input: str, analysis: Dict[str, Any]) -> List[str]:
        """Create an execution plan based on the task analysis."""
        if analysis.get("complexity") == "complex":
            return [
                "Analyze request thoroughly",
                "Break down into sub-tasks",
                "Delegate to appropriate sub-agents",
                "Coordinate execution",
                "Synthesize results"
            ]
        elif analysis.get("complexity") == "moderate":
            return [
                "Analyze request",
                "Execute with available tools",
                "Save context if needed",
                "Provide comprehensive response"
            ]
        else:
            return [
                "Process request directly",
                "Provide immediate response"
            ]
    

    

    
    def _analyze_request_type(self, user_input: str) -> str:
        """Analyze the type of request to determine appropriate formatting."""
        budget_keywords = ["budget", "cost", "expense", "money", "price", "financial", "breakdown", "spend"]
        planning_keywords = ["plan", "trip", "itinerary", "schedule", "organize", "arrange", "prepare"]
        analysis_keywords = ["analyze", "compare", "evaluate", "assess", "review", "study", "examine"]
        
        if any(keyword in user_input for keyword in budget_keywords):
            return "budget"
        elif any(keyword in user_input for keyword in planning_keywords):
            return "planning"
        elif any(keyword in user_input for keyword in analysis_keywords):
            return "analysis"
        else:
            return "essay"
    
    def run(self, user_input: str) -> Dict[str, Any]:
        """Main execution method for the supervisor agent."""
        return self.run_with_context(user_input, [])
    
    def run_with_context(self, user_input: str, conversation_history: list) -> Dict[str, Any]:
        """Main execution method with conversation context."""
        try:
            # Build context from conversation history
            context_str = self._build_context(conversation_history)
            
            # Step 1: Analyze the task
            analysis = self.analyze_task(user_input)
            
            # Step 2: Plan execution
            plan = self.plan_execution(user_input, analysis)
            
            # Step 3: Execute the task with context
            result = self.execute_task_with_context(user_input, context_str)
            
            # Step 4: Return comprehensive result
            # Ensure result has required keys
            if not isinstance(result, dict):
                result = {"success": False, "response": "Invalid result format", "tools_used": 0}
            
            success = result.get("success", False)
            response = result.get("response", "No response generated")
            tools_used = result.get("tools_used", 0)
            
            return {
                "success": success,
                "final_response": response,
                "tools_used": tools_used,
                "execution_plan": plan,
                "analysis": analysis.get("analysis", "Task analyzed successfully"),
                "delegated_to": result.get("delegated_to")
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG - Error in run_with_context: {error_details}")  # Debug log
            return {
                "success": False,
                "final_response": f"I encountered an error: {str(e)}",
                "tools_used": 0,
                "error": str(e)
            }
    
    def _build_context(self, conversation_history: list) -> str:
        """Build context string from conversation history."""
        if not conversation_history or len(conversation_history) < 2:
            return ""
        
        # Get last few exchanges (excluding current message)
        recent_history = conversation_history[-6:-1] if len(conversation_history) > 1 else []
        
        if not recent_history:
            return ""
        
        context_parts = []
        for msg in recent_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:200]  # Limit length
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def execute_task_with_context(self, user_input: str, context: str) -> Dict[str, Any]:
        """Execute task with conversation context and delegation capabilities."""
        try:
            # Determine request type
            request_type = self._analyze_request_type(user_input.lower())
            
            # Check if task should be delegated
            delegation_analysis = analyze_task_for_delegation(user_input)
            should_delegate = delegation_analysis["confidence"] > 0.15  # Lower threshold for better delegation
            
            tools_used = 0
            
            if should_delegate and delegation_analysis["recommended_agent"]:
                # Delegate to specialized agent
                recommended_agent = delegation_analysis["recommended_agent"]
                
                if recommended_agent == "SummarizerAgent":
                    # Extract content if available from context or ask for it
                    content = self._extract_content_from_context(context, user_input)
                    delegation_result = delegate_to_summarizer.invoke({
                        "task": user_input,
                        "content": content
                    })
                    tools_used += 1
                    
                elif recommended_agent == "SearchAgent":
                    delegation_result = delegate_to_search_agent.invoke({
                        "task": user_input
                    })
                    tools_used += 1
                
                if delegation_result.get("success"):
                    agent_result = delegation_result["result"]
                    if agent_result.get("success"):
                        # Format the delegated response
                        response = f"I've delegated this task to my {recommended_agent} specialist.\n\n"
                        
                        if "summary" in agent_result:
                            response += agent_result["summary"]
                        elif "research_results" in agent_result:
                            response += agent_result["research_results"]
                        else:
                            response += agent_result.get("result", "Task completed by specialist.")
                        
                        response += f"\n\n*Task handled by: {recommended_agent}*"
                        
                        return {
                            "success": True,
                            "response": response,
                            "tools_used": tools_used,
                            "delegated_to": recommended_agent
                        }
            
            # Handle task directly if not delegated
            # Build input with context
            if context:
                full_input = f"""Previous conversation:
{context}

Current request: {user_input}

Based on our conversation, provide a helpful, complete response. Don't just ask more questions - give practical, actionable advice or solutions."""
            else:
                # No context, provide direct help based on request type
                if request_type == "budget":
                    full_input = f"{user_input}\n\nProvide a practical budget breakdown with specific numbers, categories, and actionable advice."
                elif request_type == "planning":
                    full_input = f"{user_input}\n\nCreate a detailed, practical plan with specific steps, timeline, and actionable guidance."
                elif request_type == "analysis":
                    full_input = f"{user_input}\n\nProvide a clear, comprehensive analysis with key insights and actionable recommendations."
                else:
                    # For simple requests like invitations, provide actual templates/examples
                    if "invite" in user_input.lower() or "invitation" in user_input.lower():
                        full_input = f"{user_input}\n\nProvide actual invitation text or templates that the user can use immediately. Be specific and helpful."
                    else:
                        full_input = f"{user_input}\n\nProvide a helpful, complete response with practical advice and specific guidance."
            
            # Get LLM response
            response = self.chain.invoke({"input": full_input})
            
            # Keep response natural and clean
            enhanced_response = response.strip()
            
            # Auto-save longer responses with better naming
            if len(enhanced_response) > 800:
                # Create meaningful filename based on content
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Try to extract topic from user input for better naming
                topic_words = user_input.lower().split()[:3]
                topic = "_".join(word for word in topic_words if word.isalnum())[:20]
                
                if topic:
                    filename = f"conversation_{topic}_{timestamp}.txt"
                else:
                    filename = f"conversation_{timestamp}.txt"
                
                content = f"User: {user_input}\n\nAssistant: {enhanced_response}"
                
                result = vfs_write_file.invoke({"filename": filename, "content": content})
                if result.get("success"):
                    tools_used += 1
            
            return {
                "success": True,
                "response": enhanced_response,
                "tools_used": tools_used
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}",
                "tools_used": 0
            }
    
    def _extract_content_from_context(self, context: str, user_input: str) -> str:
        """Extract content for summarization from context or user input."""
        # Look for content in the conversation context
        if context and len(context) > 200:
            return context
        
        # Check if user provided content directly
        content_indicators = ["summarize this:", "analyze this:", "review this:"]
        for indicator in content_indicators:
            if indicator in user_input.lower():
                content_start = user_input.lower().find(indicator) + len(indicator)
                return user_input[content_start:].strip()
        
        return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the supervisor agent."""
        # Get VFS stats
        vfs = get_vfs()
        vfs_stats = vfs.get_stats()
        
        return {
            "agent_type": "supervisor",
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY")),
            "framework": "LangChain + Groq",
            "vfs_status": {
                "total_files": vfs_stats.get("stats", {}).get("total_files", 0),
                "persistent": vfs.enable_persistence if hasattr(vfs, 'enable_persistence') else False
            },
            "capabilities": [
                "Task analysis and planning",
                "Sub-agent coordination",
                "Persistent memory management",
                "Workflow orchestration",
                "File management"
            ]
        }
    
    def clean_vfs(self) -> Dict[str, Any]:
        """Clean up temporary files in VFS."""
        try:
            vfs = get_vfs()
            # Clean up chat/conversation files
            temp_files = [f for f in vfs.files.keys() if f.startswith('chat_') or f.startswith('conversation_')]
            deleted_count = 0
            
            for filename in temp_files:
                result = vfs.delete_file(filename)
                if result['success']:
                    deleted_count += 1
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Cleaned up {deleted_count} temporary files"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to clean VFS: {str(e)}"
            }


# Global state management (moved from main agent file)
_current_agent_state = None

def get_current_agent_state():
    """Get the current agent state for tools to access."""
    return _current_agent_state

def update_agent_state(section: str, key: str, value: Any) -> bool:
    """Update a specific section of the agent state."""
    global _current_agent_state
    try:
        if _current_agent_state is None:
            _current_agent_state = {
                "virtual_files": {},
                "todos": [],
                "current_todo_id": None,
                "step_count": 0,
                "max_steps": 10
            }
        
        if section == "virtual_files":
            _current_agent_state["virtual_files"][key] = value
        elif section in _current_agent_state:
            _current_agent_state[section] = value
        
        return True
    except Exception:
        return False