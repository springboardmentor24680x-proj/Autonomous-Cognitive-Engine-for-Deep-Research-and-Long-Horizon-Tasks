#!/usr/bin/env python3
"""
Supervisor Agent - Main orchestrator for multi-agent workflow automation
Coordinates task planning, sub-agent delegation, and memory management
"""

import os
import time
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Import tools from the tools module
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls
from tools.search_tool import web_search
from tools.delegation_tool import (
    delegate_to_summarizer, 
    delegate_to_search_agent,
    delegate_to_code_agent,
    delegate_to_planning_agent,
    delegate_to_creative_agent,
    delegate_to_translation_agent,
    create_todo_item,
    analyze_delegation_need,
    analyze_task_for_delegation,
    get_available_agents
)
from tools.todo_management import (
    write_todos, get_next_todo, complete_todo, get_todo_status, 
    synthesize_todo_results, reset_todo_workflow
)
from memory.vfs import get_current_agent_state, update_agent_state, get_vfs
from memory.conversation_memory import get_conversation_memory


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
            max_tokens=2000  # Increased for better large dataset handling
        )
        
        self.model = model_name
        self.conversation_memory = get_conversation_memory()
        
        # Initialize agent state
        self._initialize_state()
        
        # Set up tools for tracing
        self.tools = {
            'vfs_write_file': vfs_write_file,
            'vfs_read_file': vfs_read_file,
            'vfs_ls': vfs_ls,
            'web_search': web_search,
            'analyze_delegation_need': analyze_delegation_need,
            'delegate_to_summarizer': delegate_to_summarizer,
            'delegate_to_search_agent': delegate_to_search_agent,
            'delegate_to_code_agent': delegate_to_code_agent,
            'delegate_to_planning_agent': delegate_to_planning_agent,
            'delegate_to_creative_agent': delegate_to_creative_agent,
            'delegate_to_translation_agent': delegate_to_translation_agent,
            'create_todo_item': create_todo_item
        }
        
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
        
        return f"""You are an advanced AI assistant designed to provide helpful, accurate, and professional responses. You have access to specialized agents and external tools to deliver comprehensive solutions.

{current_info}

RESPONSE STYLE & TONE:
- Professional yet conversational, like ChatGPT
- Clear, well-structured, and easy to understand
- Confident but humble when uncertain
- Helpful and solution-oriented
- Engaging and personable without being overly casual

RESPONSE STRUCTURE - USE MARKDOWN:
- Use ## for main sections, ### for subsections
- Use **bold** for emphasis and key points
- Use bullet points (-) for lists and options
- Use numbered lists (1. 2. 3.) for sequential steps
- Use `code` for inline code and technical terms
- Use ```language for code blocks ONLY when the user asks for code
- Add proper spacing between sections (blank lines)
- Use > for important notes or quotes
- Use tables when comparing data

CRITICAL RULES:
1. **ONLY provide code when explicitly requested** - Don't add code examples to summaries, explanations, or general responses
2. **Match your response to the request type**:
   - Summarization → Provide summary only, no code
   - Research → Provide findings and insights, no code
   - Translation → Provide translations only, no code
   - Code request → Provide code with explanations
   - Planning → Provide plans and strategies, no code
3. **Stay focused** - Answer what was asked, don't add unrelated content
4. **Be concise** - Provide complete but not excessive information

RESPONSE APPROACH:
- Analyze the request thoroughly
- Provide complete, actionable solutions
- Include relevant examples ONLY when appropriate to the request type
- Use proper markdown formatting for readability
- Anticipate follow-up questions and address them proactively
- Offer additional resources or next steps when relevant

CAPABILITIES TO LEVERAGE:
- Strategic planning and project management
- Code generation and technical solutions (when requested)
- Research and analysis
- Content creation and writing
- Translation and localization
- File operations and data analysis
- Web search and real-time information

Always strive to be genuinely helpful while maintaining a professional, knowledgeable, and approachable tone similar to ChatGPT. Format all responses with clean markdown for optimal readability. NEVER add code examples unless the user specifically asks for code."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def _invoke_tool_with_tracing(self, tool_name: str, tool_input: Dict[str, Any], user_input: str = "") -> Dict[str, Any]:
        """Invoke a tool with proper LangSmith tracing."""
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found",
                    "result": None
                }
            
            tool = self.tools[tool_name]
            
            # Add metadata for better tracing visibility
            from langsmith import traceable
            
            # Create a traceable wrapper with explicit naming
            @traceable(
                run_type="tool",
                name=f"Tool: {tool_name}",
                metadata={
                    "tool_name": tool_name,
                    "tool_type": "delegation" if "delegate" in tool_name else "utility",
                    "input_keys": list(tool_input.keys()),
                    "tool_input": str(tool_input)[:500],  # Include input (truncated to 500 chars)
                    "user_input": user_input[:200] if user_input else "No user input provided"  # Include user input
                },
                tags=["tool_invocation", "delegation" if "delegate" in tool_name else "utility"]
            )
            def invoke_with_metadata(original_input: str):  # ← Parameter shows in Input tab
                return tool.invoke(tool_input)
            
            # Invoke the tool with tracing
            result = invoke_with_metadata(user_input or "No user input")
            
            return {
                "success": True,
                "tool_name": tool_name,
                "tool_input": tool_input,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "tool_input": tool_input,
                "result": None
            }
    
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
    
    def run_with_context(self, user_input: str, conversation_history: list, session_id: str = None) -> Dict[str, Any]:
        """Main execution method with conversation context and memory tracking."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name=" Supervisor Agent - Main Execution",
            metadata={
                "session_id": session_id, 
                "has_history": len(conversation_history) > 0,
                "input_length": len(user_input),
                "workflow_type": "traditional",  # Will be updated if TODO workflow runs
                "expected_complexity": "moderate"
            },
            tags=["supervisor", "main_execution"]
        )
        def execute_with_tracing(user_query: str):  # ← Parameter shows in Input tab
            try:
                # Initialize session if needed
                nonlocal session_id
                if session_id is None:
                    session_id = self.conversation_memory.create_session()
                elif session_id not in self.conversation_memory.current_sessions:
                    self.conversation_memory.create_session(session_id)
                
                # Add user message to conversation memory
                self.conversation_memory.add_message(session_id, 'user', user_query)
                
                # Get enhanced context from conversation memory
                memory_context = self.conversation_memory.get_conversation_context(session_id, max_messages=10)
                session_summary = self.conversation_memory.get_session_summary(session_id)
                
                # Build enhanced context
                context_str = self._build_enhanced_context(memory_context, session_summary)
                
                # Step 1: Analyze the task
                analysis = self.analyze_task(user_query)
                
                # Step 2: Plan execution
                plan = self.plan_execution(user_query, analysis)
                
                # Step 3: Execute the task with enhanced context
                result = self.execute_task_with_enhanced_context(user_query, context_str, session_id)
                
                # Step 4: Add assistant response to conversation memory
                if result.get("success"):
                    self.conversation_memory.add_message(
                        session_id, 
                        'assistant', 
                        result.get("response", ""),
                        agent_used=result.get("delegated_to"),
                        tools_used=result.get("tools_used", 0)
                    )
                
                # Step 5: Return comprehensive result
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
                    "delegated_to": result.get("delegated_to"),
                    "session_id": session_id,
                    "conversation_context": len(memory_context),
                    "session_summary": session_summary,
                    "workflow": result.get("workflow", "traditional"),
                    "todos_created": result.get("todos_created", 0),
                    "todos_completed": result.get("todos_completed", 0),
                    "todo_breakdown": result.get("todo_breakdown", []),
                    "todos_file": result.get("todos_file"),
                    "synthesis_file": result.get("synthesis_file")
                }
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"DEBUG - Error in run_with_context: {error_details}")  # Debug log
                return {
                    "success": False,
                    "final_response": f"I encountered an error: {str(e)}",
                    "tools_used": 0,
                    "error": str(e),
                    "session_id": session_id
                }
        
        return execute_with_tracing(user_input)  # ← Pass user_input as parameter
    
    def _build_enhanced_context(self, memory_context: List[Dict[str, Any]], session_summary: Dict[str, Any]) -> str:
        """Build enhanced context from conversation memory."""
        if not memory_context:
            return ""
        
        context_parts = []
        
        # Add session summary if available
        if session_summary.get('context_summary'):
            context_parts.append(f"Session Context: {session_summary['context_summary']}")
        
        # Add user preferences if available
        if session_summary.get('user_preferences'):
            prefs = session_summary['user_preferences']
            if prefs:
                context_parts.append(f"User Preferences: {', '.join([f'{k}: {v}' for k, v in prefs.items()])}")
        
        # Add recent conversation
        context_parts.append("Recent Conversation:")
        for msg in memory_context[-6:]:  # Last 6 messages
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:150]  # Limit length
            agent_info = f" (via {msg['agent_used']})" if msg.get('agent_used') else ""
            context_parts.append(f"{role}{agent_info}: {content}")
        
        return "\n".join(context_parts)
    
    def execute_task_with_enhanced_context(self, user_input: str, context: str, session_id: str) -> Dict[str, Any]:
        """Execute task with enhanced conversation context and memory."""
        try:
            # Get conversation insights for personalization
            insights = self.conversation_memory.get_conversation_insights(session_id)
            
            # Determine request type
            request_type = self._analyze_request_type(user_input.lower())
            
            # Check for simple factual questions that should be handled directly
            simple_factual_patterns = [
                "what is the capital of", "what is the population of", "who is the president of",
                "when was", "where is", "how many", "what does", "define", "meaning of"
            ]
            
            is_simple_factual = any(pattern in user_input.lower() for pattern in simple_factual_patterns)
            
            # Check if task should be delegated
            delegation_analysis = analyze_task_for_delegation(user_input)
            
            # For complex planning tasks, use TODO workflow instead of direct delegation
            if (delegation_analysis.get("recommended_agent") == "PlanningAgent" and 
                self._should_create_todos(user_input)):
                should_delegate = False  # Force TODO workflow for complex planning
            else:
                # Use higher threshold for delegation and handle simple questions directly
                should_delegate = (
                    delegation_analysis["confidence"] >= 0.4 and  # Moderate threshold (inclusive)
                    not is_simple_factual and  # Don't delegate simple factual questions
                    len(user_input.split()) > 3  # Don't delegate very short questions
                )
            
            tools_used = 0
            
            # Handle simple factual questions directly with conversation awareness
            if is_simple_factual and len(user_input.split()) <= 10:
                # Build input for direct response with conversation context
                full_input = f"{user_input}\n\nProvide a direct, factual answer."
                
                # Add conversation style adaptation
                if insights.get('interaction_patterns', {}).get('conversation_style') == 'detailed':
                    full_input += " The user prefers detailed explanations."
                
                # Get LLM response directly
                response = self.chain.invoke({"input": full_input})
                
                return {
                    "success": True,
                    "response": response.strip(),
                    "tools_used": 0
                }
            
            # For complex tasks that need delegation, use tool invocation with tracing
            if should_delegate:
                from langsmith import traceable
                
                @traceable(
                    run_type="chain",
                    name=f" Task Delegation Analysis",
                    metadata={
                        "task": user_input[:100],
                        "task_length": len(user_input.split()),
                        "delegation_confidence": delegation_analysis.get("confidence", 0)
                    },
                    tags=["delegation", "analysis"]
                )
                def analyze_and_delegate():
                    # STEP 1: Create explicit TODO for delegation task
                    recommended_agent = delegation_analysis.get('recommended_agent')
                    
                    # Create structured TODO list for LangSmith tracking
                    todo_item = {
                        "id": f"todo_{int(time.time())}",
                        "task": user_input,
                        "assigned_agent": recommended_agent,
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Store TODO in trace metadata for LangSmith visibility
                    todo_breakdown = [todo_item]
                    
                    print(f"[TODO CREATED] {todo_item['id']}: {user_input[:50]}... → {recommended_agent}")
                    
                    # STEP 2: Delegate to the appropriate agent
                    # First analyze the delegation need with tracing
                    analysis_result = self._invoke_tool_with_tracing(
                        'analyze_delegation_need', 
                        {'task': user_input},
                        user_input  # Pass user input for tracing
                    )
                    
                    if not analysis_result['success']:
                        # Mark TODO as failed
                        todo_item["status"] = "failed"
                        todo_item["error"] = "Delegation analysis failed"
                        return None, 1, todo_breakdown
                    
                    delegation_info = analysis_result['result']
                    recommended_agent = delegation_info.get('recommended_agent')
                    
                    # Map agent names to tool names
                    agent_to_tool = {
                        'SummarizerAgent': 'delegate_to_summarizer',
                        'SearchAgent': 'delegate_to_search_agent',
                        'CodeAgent': 'delegate_to_code_agent',
                        'PlanningAgent': 'delegate_to_planning_agent',
                        'CreativeAgent': 'delegate_to_creative_agent',
                        'TranslationAgent': 'delegate_to_translation_agent'
                    }
                    
                    if recommended_agent not in agent_to_tool:
                        # Mark TODO as failed
                        todo_item["status"] = "failed"
                        todo_item["error"] = f"Unknown agent: {recommended_agent}"
                        return None, 1, todo_breakdown
                    
                    tool_name = agent_to_tool[recommended_agent]
                    
                    # Update TODO status to in_progress
                    todo_item["status"] = "in_progress"
                    todo_item["started_at"] = datetime.now().isoformat()
                    
                    print(f"[TODO IN PROGRESS] {todo_item['id']}: Delegating to {recommended_agent}")
                    
                    # Prepare tool input based on agent type
                    if recommended_agent == 'SummarizerAgent':
                        content = self._extract_content_from_context(context, user_input)
                        tool_input = {'task': user_input, 'content': content}
                    elif recommended_agent in ['CodeAgent', 'PlanningAgent', 'CreativeAgent']:
                        extracted_context = self._extract_content_from_context(context, user_input)
                        if recommended_agent == 'CodeAgent':
                            tool_input = {'task': user_input, 'code_context': extracted_context}
                        else:
                            tool_input = {'task': user_input, 'context': extracted_context}
                    elif recommended_agent == 'TranslationAgent':
                        content = self._extract_content_from_context(context, user_input)
                        tool_input = {'task': user_input, 'content': content}
                    else:
                        tool_input = {'task': user_input}
                    
                    # Invoke delegation tool with tracing
                    delegation_result = self._invoke_tool_with_tracing(tool_name, tool_input, user_input)
                    
                    # STEP 3: Update TODO status based on delegation result
                    if delegation_result['success']:
                        todo_item["status"] = "completed"
                        todo_item["completed_at"] = datetime.now().isoformat()
                        todo_item["result"] = "Delegation successful"
                        print(f"[TODO COMPLETED] {todo_item['id']}: Successfully delegated to {recommended_agent}")
                    else:
                        todo_item["status"] = "failed"
                        todo_item["failed_at"] = datetime.now().isoformat()
                        todo_item["error"] = delegation_result.get('error', 'Delegation failed')
                        print(f"[TODO FAILED] {todo_item['id']}: Delegation failed - {todo_item['error']}")
                    
                    return (delegation_result, recommended_agent), 2, todo_breakdown
                
                result_tuple, tools_count, todo_breakdown = analyze_and_delegate()
                tools_used += tools_count
                
                if result_tuple:
                    delegation_result, recommended_agent = result_tuple
                    
                    if delegation_result.get('success'):
                        agent_result = delegation_result['result']  # This is the delegation tool result
                        
                        # Handle the delegation tool result structure
                        if isinstance(agent_result, dict) and agent_result.get('success'):
                            # Use the existing _extract_agent_response method which handles all agent types
                            response = self._extract_agent_response(agent_result, recommended_agent)
                            
                            # If extraction failed or returned default, try direct result key
                            if not response or response == "Task completed by specialist." or len(response) < 50:
                                # The delegation tool wraps the agent result in a "result" key
                                # So we need to look at agent_result["result"] for the actual agent response
                                nested_result = agent_result.get('result', {})
                                if isinstance(nested_result, dict):
                                    # Try to extract from the nested agent result
                                    if recommended_agent == "SearchAgent":
                                        # SearchAgent returns research_results, trend_analysis, market_research, or fact_check
                                        response = (nested_result.get('research_results') or 
                                                  nested_result.get('trend_analysis') or 
                                                  nested_result.get('market_research') or 
                                                  nested_result.get('fact_check') or 
                                                  str(nested_result))
                                    elif recommended_agent == "PlanningAgent":
                                        response = (nested_result.get('project_plan') or 
                                                  nested_result.get('strategy') or 
                                                  nested_result.get('task_breakdown') or 
                                                  nested_result.get('timeline') or 
                                                  str(nested_result))
                                    else:
                                        # Try to find any meaningful content in the nested result
                                        for key, value in nested_result.items():
                                            if isinstance(value, str) and len(value) > 50 and key not in ["agent_type", "error", "success"]:
                                                response = value
                                                break
                                        else:
                                            response = str(nested_result)
                                elif isinstance(nested_result, str) and len(nested_result) > len(user_input):
                                    response = nested_result
                                else:
                                    response = f"Task processed by {recommended_agent}"
                        elif isinstance(agent_result, str) and len(agent_result) > len(user_input):
                            # Direct string result
                            response = agent_result
                        else:
                            # Fallback - convert to string but this shouldn't happen for successful delegations
                            response = str(agent_result) if agent_result else f"Task processed by {recommended_agent}"
                        
                        # Ensure response is a string before concatenation
                        if not isinstance(response, str):
                            response = str(response)
                        
                        # Add subtle attribution
                        response += f"\n\n---\n*Powered by {recommended_agent}*"
                        
                        return {
                            "success": True,
                            "response": response,
                            "tools_used": tools_used,
                            "delegated_to": recommended_agent,
                            "workflow": "delegation_with_todos",
                            "todos_created": 1,
                            "todos_completed": 1 if todo_breakdown[0]["status"] == "completed" else 0,
                            "todo_breakdown": todo_breakdown,
                            "todos_file": f"delegation_todo_{todo_breakdown[0]['id']}.json"
                        }
            
            # Continue with existing direct execution logic for non-delegated tasks
            return self._execute_direct_task_with_todos(user_input, context)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}",
                "tools_used": 0
            }
    
    def _execute_direct_task_with_todos(self, user_input: str, context: str) -> Dict[str, Any]:
        """Execute direct tasks with explicit TODO tracking for LangSmith."""
        # Check if this should be a complex TODO workflow
        should_create_todos = self._should_create_todos(user_input)
        
        if should_create_todos:
            # Use the existing TODO workflow
            return self._execute_todo_workflow(user_input, context)
        else:
            # Create a simple TODO for direct execution
            todo_item = {
                "id": f"direct_todo_{int(time.time())}",
                "task": user_input,
                "assigned_agent": "SupervisorAgent",
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            print(f"[TODO CREATED] {todo_item['id']}: {user_input[:50]}... → SupervisorAgent (Direct)")
            
            # Mark as in progress
            todo_item["status"] = "in_progress"
            todo_item["started_at"] = datetime.now().isoformat()
            
            # Execute the task directly
            result = self._process_single_task(user_input, context)
            
            # Update TODO status
            if result.get("success"):
                todo_item["status"] = "completed"
                todo_item["completed_at"] = datetime.now().isoformat()
                todo_item["result"] = "Direct execution successful"
                print(f"[TODO COMPLETED] {todo_item['id']}: Direct execution successful")
            else:
                todo_item["status"] = "failed"
                todo_item["failed_at"] = datetime.now().isoformat()
                todo_item["error"] = result.get("error", "Direct execution failed")
                print(f"[TODO FAILED] {todo_item['id']}: {todo_item['error']}")
            
            # Add TODO information to result
            result["todos_created"] = 1
            result["todos_completed"] = 1 if todo_item["status"] == "completed" else 0
            result["todo_breakdown"] = [todo_item]
            result["todos_file"] = f"direct_todo_{todo_item['id']}.json"
            result["workflow"] = result.get("workflow", "traditional")
            
            return result
    
    def _should_create_todos(self, user_input: str) -> bool:
        """Determine if a task should be broken down into TODOs."""
        task_lower = user_input.lower()
        
        # Complex project indicators
        complex_project_indicators = [
            "comprehensive project plan", "complete project", "full project plan",
            "step by step plan", "detailed plan", "strategic plan", "roadmap",
            "complete analysis and plan", "research and develop", "design and implement"
        ]
        
        # Multi-step task indicators
        multi_step_indicators = [
            "first", "then", "finally", "next", "after that", "followed by",
            "research", "analyze", "create", "develop", "implement", "design",
            "and then", "step by step", "phases", "stages"
        ]
        
        # Sequential task patterns
        sequential_patterns = [
            "research.*analyze.*create", "analyze.*create.*report", 
            "first.*then.*finally", "research.*then.*analyze",
            "create.*and.*analyze", "develop.*and.*implement"
        ]
        
        # Complex task types that need breakdown
        complex_tasks = [
            "comprehensive", "detailed", "complete", "full", "strategic",
            "multi-step", "complex", "thorough", "in-depth"
        ]
        
        # Check for explicit project planning requests
        is_explicit_project = any(indicator in task_lower for indicator in complex_project_indicators)
        
        # Check for multi-step indicators
        has_multi_step = sum(1 for indicator in multi_step_indicators if indicator in task_lower) >= 2
        
        # Check for sequential patterns using regex
        import re
        has_sequential_pattern = any(re.search(pattern, task_lower) for pattern in sequential_patterns)
        
        # Check for complex task types
        is_complex_task = any(task_type in task_lower for task_type in complex_tasks)
        
        # Check word count (longer tasks are more likely to need breakdown)
        word_count = len(user_input.split())
        is_long_task = word_count > 15
        
        # Create TODOs if:
        # 1. Explicit project request, OR
        # 2. Has multi-step indicators AND is complex/long, OR
        # 3. Has sequential patterns, OR
        # 4. Very long task (50+ words) with planning keywords
        return (is_explicit_project or 
                (has_multi_step and (is_complex_task or is_long_task)) or
                has_sequential_pattern or
                (word_count > 50 and any(keyword in task_lower for keyword in ["project", "plan", "strategy", "roadmap"])))
    
    def _create_todos_for_task(self, user_input: str) -> List[str]:
        """Create TODO items for a complex task."""
        try:
            # Use the create_todo_item tool to break down the task
            breakdown_prompt = f"""Break down this complex task into 3-4 specific, actionable TODO items:

Task: {user_input}

Return ONLY a numbered list of 3-4 specific sub-tasks, one per line:
1. [First specific action]
2. [Second specific action]
3. [Third specific action]
4. [Fourth specific action]

Make each TODO item specific and actionable. Keep it to maximum 4 items."""

            # Get breakdown from LLM
            breakdown_result = self.chain.invoke({"input": breakdown_prompt})
            
            # Parse the breakdown into TODO items
            lines = breakdown_result.strip().split('\n')
            todos = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    todo_text = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('- ').strip()
                    if todo_text and len(todo_text) > 5:  # Ensure meaningful TODO
                        todos.append(todo_text)
            
            # Ensure we have at least one TODO
            if not todos:
                todos = [user_input]
            
            # Create actual TODO items using the tool
            created_todos = []
            for i, todo_text in enumerate(todos[:3], 1):  # Limit to 3 TODOs maximum
                todo_result = self._invoke_tool_with_tracing(
                    'create_todo_item',
                    {'task': todo_text, 'priority': 'medium'},
                    user_input  # Pass user input for tracing
                )
                if todo_result['success']:
                    created_todos.append(todo_text)
            
            return created_todos
            
        except Exception as e:
            print(f"Error creating TODOs: {e}")
            return [user_input]  # Fallback to single TODO
    
    def execute_task_with_context(self, user_input: str, context: str) -> Dict[str, Any]:
        """Execute task with conversation context and proper TODO workflow."""
        try:
            # Check if this task should be broken down into TODOs
            should_create_todos = self._should_create_todos(user_input)
            
            if should_create_todos:
                return self._execute_todo_workflow(user_input, context)
            
            # For non-TODO tasks, use existing logic
            return self._process_single_task(user_input, context)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}",
                "tools_used": 0
            }
    
    def _execute_todo_workflow(self, user_input: str, context: str) -> Dict[str, Any]:
        """Execute the TODO workflow with proper tracing."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="TODO Workflow Execution",
            metadata={
                "task": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                "workflow_type": "TODO_VFS_WORKFLOW",
                "has_context": len(context) > 0
            },
            tags=["todo_workflow", "complex_task"]
        )
        def execute_todo_workflow_with_tracing(task_description: str):
            # STEP 1: PLAN - Create TODOs using write_todos tool
            created_todos = self._create_todos_for_task(task_description)
            
            if len(created_todos) > 1:
                print(f"\n[PLAN] Creating {len(created_todos)} TODOs for complex task")
                
                # Use write_todos tool to persist TODOs
                from tools.todo_management import write_todos
                todos_result = write_todos.invoke({
                    "task_description": task_description,
                    "todo_list": created_todos
                })
                
                if not todos_result["success"]:
                    return {
                        "success": False,
                        "error": "Failed to create TODOs",
                        "response": f"Could not create TODO workflow: {todos_result.get('error', 'Unknown error')}",
                        "tools_used": 1
                    }
                
                print(f"[PLAN] TODOs saved to: {todos_result['todos_file']}")
                
                # STEP 2: EXECUTION LOOP - Process each TODO
                from tools.todo_management import get_next_todo, complete_todo
                
                tools_used = 1  # write_todos
                execution_results = []
                
                while True:
                    # Get next pending TODO
                    next_todo_result = get_next_todo.invoke({})
                    tools_used += 1
                    
                    if not next_todo_result["success"] or not next_todo_result.get("has_next", False):
                        print(f"[EXECUTION] All TODOs completed!")
                        break
                    
                    current_todo = next_todo_result["todo"]
                    todo_task = current_todo["task"]
                    todo_id = current_todo["id"]
                    
                    print(f"\n[EXECUTION] Processing TODO {next_todo_result['todo_index']+1}: {todo_task}")
                    
                    # STEP 3: REASON & ACT - Process the TODO
                    # Determine if this should be delegated or handled directly
                    original_analysis = analyze_task_for_delegation(user_input)
                    if original_analysis.get('recommended_agent') == 'PlanningAgent':
                        # Force delegation to PlanningAgent for planning tasks
                        todo_result = self._invoke_tool_with_tracing(
                            'delegate_to_planning_agent',
                            {"task": todo_task, "context": context},
                            user_input  # Pass original user input for tracing
                        )
                        if todo_result.get("success"):
                            todo_result = todo_result["result"]  # Extract the actual result
                        assigned_agent = "PlanningAgent"
                        tools_used += 1
                    else:
                        # Process normally with delegation analysis
                        todo_result = self._process_single_task(todo_task, context)
                        assigned_agent = todo_result.get("delegated_to", "SupervisorAgent")
                        tools_used += todo_result.get("tools_used", 0)
                    
                    # STEP 4: OBSERVE & UPDATE - Save result and mark complete
                    if todo_result.get("success", False):
                        result_content = todo_result.get("response", str(todo_result))
                        
                        # Complete the TODO and save result to VFS
                        complete_result = complete_todo.invoke({
                            "todo_id": todo_id,
                            "result": result_content,
                            "assigned_agent": assigned_agent
                        })
                        tools_used += 1
                        
                        if complete_result["success"]:
                            print(f"[UPDATE] TODO completed, result saved to: {complete_result['result_file']}")
                            execution_results.append({
                                "todo": todo_task,
                                "result": result_content,
                                "agent": assigned_agent,
                                "result_file": complete_result['result_file']
                            })
                        else:
                            print(f"[ERROR] Failed to complete TODO: {complete_result.get('error')}")
                    else:
                        print(f"[ERROR] TODO execution failed: {todo_result.get('error', 'Unknown error')}")
                
                # STEP 5: SYNTHESIZE - Gather all results using read_file
                print(f"\n[SYNTHESIZE] Reading all TODO results from VFS...")
                from tools.todo_management import synthesize_todo_results
                synthesis_result = synthesize_todo_results.invoke({})
                tools_used += 1
                
                if synthesis_result["success"]:
                    print(f"[SYNTHESIZE] Results synthesized to: {synthesis_result['synthesis_file']}")
                    final_response = synthesis_result["synthesis_content"]
                else:
                    # Fallback synthesis
                    final_response = self._fallback_synthesis(task_description, execution_results)
                
                return {
                    "success": True,
                    "response": final_response,
                    "tools_used": tools_used,
                    "todos_created": len(created_todos),
                    "todos_completed": len(execution_results),
                    "todo_breakdown": created_todos,
                    "workflow": "TODO_VFS_WORKFLOW",
                    "todos_file": todos_result.get("todos_file"),
                    "synthesis_file": synthesis_result.get("synthesis_file") if synthesis_result["success"] else None
                }
            
            # If only one TODO created, fall back to single task processing
            return self._process_single_task(task_description, context)
        
        return execute_todo_workflow_with_tracing(user_input)
    
    def _fallback_synthesis(self, user_input: str, execution_results: List[Dict]) -> str:
        """Fallback synthesis when VFS synthesis fails."""
        synthesis_prompt = f"""Combine these TODO results into a comprehensive response for: {user_input}

TODO Results:
"""
        for i, result in enumerate(execution_results, 1):
            synthesis_prompt += f"\n{i}. {result['todo']}\nAgent: {result['agent']}\nResult: {result['result']}\n"
        
        synthesis_prompt += "\nProvide a well-structured, comprehensive final response that integrates all the TODO results."
        
        return self.chain.invoke({"input": synthesis_prompt})
    
    def _process_single_task(self, user_input: str, context: str) -> Dict[str, Any]:
        """Process a single task (used for both individual tasks and TODO items)."""
        try:
            # Determine request type
            request_type = self._analyze_request_type(user_input.lower())
            
            # Check for simple factual questions that should be handled directly
            simple_factual_patterns = [
                "what is the capital of", "what is the population of", "who is the president of",
                "when was", "where is", "how many", "what does", "define", "meaning of"
            ]
            
            is_simple_factual = any(pattern in user_input.lower() for pattern in simple_factual_patterns)
            
            # Check if task should be delegated
            delegation_analysis = analyze_task_for_delegation(user_input)
            
            # Use higher threshold for delegation and handle simple questions directly
            should_delegate = (
                delegation_analysis["confidence"] >= 0.4 and  # Moderate threshold (inclusive)
                not is_simple_factual and  # Don't delegate simple factual questions
                len(user_input.split()) > 3  # Don't delegate very short questions
            )
            
            tools_used = 0
            
            # Handle simple factual questions directly
            if is_simple_factual and len(user_input.split()) <= 10:
                # Build input for direct response
                full_input = f"{user_input}\n\nProvide a direct, factual answer to this question."
                
                # Get LLM response directly
                response = self.chain.invoke({"input": full_input})
                
                return {
                    "success": True,
                    "response": response.strip(),
                    "tools_used": 0
                }
            
            if should_delegate and delegation_analysis["recommended_agent"]:
                # Delegate to specialized agent
                recommended_agent = delegation_analysis["recommended_agent"]
                
                if recommended_agent == "SummarizerAgent":
                    # Extract content if available from context or ask for it
                    content = self._extract_content_from_context(context, user_input)
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_summarizer',
                        {"task": user_input, "content": content},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                    
                elif recommended_agent == "SearchAgent":
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_search_agent',
                        {"task": user_input},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                    
                elif recommended_agent == "CodeAgent":
                    # Extract code context if available
                    code_context = self._extract_content_from_context(context, user_input)
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_code_agent',
                        {"task": user_input, "code_context": code_context},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                    
                elif recommended_agent == "PlanningAgent":
                    # Extract planning context if available
                    planning_context = self._extract_content_from_context(context, user_input)
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_planning_agent',
                        {"task": user_input, "context": planning_context},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                    
                elif recommended_agent == "CreativeAgent":
                    # Extract creative context if available
                    creative_context = self._extract_content_from_context(context, user_input)
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_creative_agent',
                        {"task": user_input, "context": creative_context},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                    
                elif recommended_agent == "TranslationAgent":
                    # Extract content for translation if available
                    translation_content = self._extract_content_from_context(context, user_input)
                    delegation_result = self._invoke_tool_with_tracing(
                        'delegate_to_translation_agent',
                        {"task": user_input, "content": translation_content},
                        user_input
                    )
                    if delegation_result.get("success"):
                        delegation_result = delegation_result["result"]  # Extract the actual result
                    tools_used += 1
                
                if 'delegation_result' in locals() and delegation_result.get("success"):
                    agent_result = delegation_result["result"]
                    
                    # Handle both dictionary and string results
                    if isinstance(agent_result, dict) and agent_result.get("success"):
                        # Return the agent's response directly without delegation message
                        response = ""
                        
                        if "summary" in agent_result:
                            response = agent_result["summary"]
                        elif "research_results" in agent_result:
                            response = agent_result["research_results"]
                        elif "trend_analysis" in agent_result:
                            response = agent_result["trend_analysis"]
                        elif "market_research" in agent_result:
                            response = agent_result["market_research"]
                        elif "fact_check" in agent_result:
                            response = agent_result["fact_check"]
                        elif "code_solution" in agent_result:
                            response = agent_result["code_solution"]
                        elif "project_plan" in agent_result:
                            response = agent_result["project_plan"]
                        elif "strategy" in agent_result:
                            response = agent_result["strategy"]
                        elif "task_breakdown" in agent_result:
                            response = agent_result["task_breakdown"]
                        elif "timeline" in agent_result:
                            response = agent_result["timeline"]
                        elif "analysis" in agent_result:
                            response = agent_result["analysis"]
                        elif "statistics" in agent_result:
                            response = agent_result["statistics"]
                        elif "insights" in agent_result:
                            response = agent_result["insights"]
                        elif "blog_post" in agent_result:
                            response = agent_result["blog_post"]
                        elif "marketing_copy" in agent_result:
                            response = agent_result["marketing_copy"]
                        elif "social_content" in agent_result:
                            response = agent_result["social_content"]
                        elif "email_template" in agent_result:
                            response = agent_result["email_template"]
                        elif "creative_story" in agent_result:
                            response = agent_result["creative_story"]
                        elif "content_ideas" in agent_result:
                            response = agent_result["content_ideas"]
                        elif "creative_content" in agent_result:
                            response = agent_result["creative_content"]
                        elif "translation" in agent_result:
                            response = agent_result["translation"]
                        elif "translated_document" in agent_result:
                            response = agent_result["translated_document"]
                        elif "localized_content" in agent_result:
                            response = agent_result["localized_content"]
                        elif "multilingual_content" in agent_result:
                            # Format multilingual content nicely
                            multilingual = agent_result["multilingual_content"]
                            if isinstance(multilingual, dict):
                                response = "**Multilingual Content:**\n\n"
                                for lang, content in multilingual.items():
                                    response += f"**{lang.title()}:**\n{content}\n\n"
                            else:
                                response = str(multilingual)
                        elif "quality_assessment" in agent_result:
                            response = agent_result["quality_assessment"]
                        else:
                            # Fallback: try to find any text content
                            for key, value in agent_result.items():
                                if isinstance(value, str) and len(value) > 50 and key not in ["agent_type", "error"]:
                                    response = value
                                    break
                            else:
                                response = agent_result.get("result", "Task completed by specialist.")
                    
                    elif isinstance(agent_result, str):
                        # Direct string result (like from PlanningAgent)
                        response = agent_result
                    
                    else:
                        # Fallback for other types
                        response = str(agent_result)
                    
                    # Ensure response is a string before concatenation
                    if not isinstance(response, str):
                        response = str(response)
                    
                    # Add subtle attribution at the end
                    response += f"\n\n---\n*Powered by {recommended_agent}*"
                    
                    return {
                        "success": True,
                        "response": response,
                        "tools_used": tools_used,
                        "delegated_to": recommended_agent
                    }
            
            # Handle task directly if not delegated
            # Build input with context
            if context:
                full_input = f"Previous conversation:\n{context}\n\nCurrent request: {user_input}\n\nBased on our conversation, provide a helpful, complete response. Don't just ask more questions - give practical, actionable advice or solutions."
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
        """Extract content for analysis from context or user input."""
        # Look for content in the conversation context
        if context and len(context) > 200:
            return context
        
        # Check if user provided content directly in their input
        content_indicators = ["summarize this:", "analyze this:", "review this:", "data:", "csv:"]
        for indicator in content_indicators:
            if indicator in user_input.lower():
                content_start = user_input.lower().find(indicator) + len(indicator)
                return user_input[content_start:].strip()
        
        # Look for CSV-like data patterns in the user input
        lines = user_input.split('\n')
        csv_lines = [line for line in lines if ',' in line and len(line.split(',')) >= 2]
        
        # If we find CSV data, extract it
        if len(csv_lines) >= 2:
            # Find the start of CSV data
            first_csv_line_index = next(i for i, line in enumerate(lines) if line in csv_lines)
            csv_data = '\n'.join(lines[first_csv_line_index:])
            return csv_data.strip()
        
        # Look for structured data after common phrases
        data_phrases = ["analyze this", "data:", "sales data", "customer data", "financial data"]
        for phrase in data_phrases:
            if phrase in user_input.lower():
                phrase_index = user_input.lower().find(phrase)
                potential_data = user_input[phrase_index + len(phrase):].strip()
                if len(potential_data) > 50 and (',' in potential_data or '\n' in potential_data):
                    return potential_data
        
        return ""
    
    def _extract_agent_response(self, agent_result: Dict[str, Any], agent_name: str) -> str:
        """Extract the main response from an agent result."""
        # The delegation tool wraps agent results in a "result" key
        # So we need to look at both the top level and nested level
        
        # First try the nested result (from delegation tool)
        nested_result = agent_result.get("result", {})
        if isinstance(nested_result, dict):
            # Try different response keys based on agent type in nested result
            response_keys = [
                "result", "plan", "summary", "research_results", "trend_analysis", "market_research", "fact_check", 
                "code_solution", "project_plan", "strategy", "task_breakdown", "timeline", 
                "analysis", "statistics", "insights", "blog_post", "marketing_copy", "social_content", 
                "email_template", "creative_story", "content_ideas", "creative_content",
                "translation", "translated_document", "localized_content", 
                "multilingual_content", "quality_assessment"
            ]
            
            for key in response_keys:
                if key in nested_result:
                    value = nested_result[key]
                    if isinstance(value, dict) and key == "multilingual_content":
                        # Format multilingual content nicely
                        response = "**Multilingual Content:**\n\n"
                        for lang, content in value.items():
                            response += f"**{lang.title()}:**\n{content}\n\n"
                        return response
                    elif isinstance(value, str) and len(value) > 50:
                        return value
            
            # If no specific keys found, try to find any meaningful text content in nested result
            for key, value in nested_result.items():
                if isinstance(value, str) and len(value) > 50 and key not in ["agent_type", "error", "success"]:
                    return value
        
        # Fallback: try the top level (original logic)
        response_keys = [
            "result", "plan", "summary", "research_results", "trend_analysis", "market_research", "fact_check", 
            "code_solution", "project_plan", "strategy", "task_breakdown", "timeline", 
            "analysis", "statistics", "insights", "blog_post", "marketing_copy", "social_content", 
            "email_template", "creative_story", "content_ideas", "creative_content",
            "translation", "translated_document", "localized_content", 
            "multilingual_content", "quality_assessment"
        ]
        
        for key in response_keys:
            if key in agent_result:
                value = agent_result[key]
                if isinstance(value, dict) and key == "multilingual_content":
                    # Format multilingual content nicely
                    response = "**Multilingual Content:**\n\n"
                    for lang, content in value.items():
                        response += f"**{lang.title()}:**\n{content}\n\n"
                    return response
                elif isinstance(value, str) and len(value) > 50:
                    return value
        
        # Fallback: try to find any text content at top level
        for key, value in agent_result.items():
            if isinstance(value, str) and len(value) > 50 and key not in ["agent_type", "error"]:
                return value
        
        return agent_result.get("result", "Task completed by specialist.")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the supervisor agent."""
        # Get VFS stats
        vfs = get_vfs()
        vfs_stats = vfs.get_stats()
        
        capabilities = [
            "Task analysis and planning",
            "Sub-agent coordination", 
            "Persistent memory management",
            "Workflow orchestration",
            "File management"
        ]
        
        return {
            "agent_type": "supervisor",
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY")),
            "framework": "LangChain + Groq",
            "vfs_status": {
                "total_files": vfs_stats.get("stats", {}).get("total_files", 0),
                "persistent": vfs.enable_persistence if hasattr(vfs, 'enable_persistence') else False
            },
            "capabilities": capabilities
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
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary for a session."""
        return self.conversation_memory.get_session_summary(session_id)
    
    def search_conversation_history(self, query: str, session_id: str = None) -> List[Dict[str, Any]]:
        """Search through conversation history."""
        return self.conversation_memory.search_conversations(query, session_id)
    
    def get_conversation_insights(self, session_id: str) -> Dict[str, Any]:
        """Get insights about conversation patterns."""
        return self.conversation_memory.get_conversation_insights(session_id)
    
    def update_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences for personalization."""
        try:
            self.conversation_memory.update_user_preferences(session_id, preferences)
            return True
        except Exception as e:
            print(f"Error updating user preferences: {e}")
            return False


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