#!/usr/bin/env python3
"""
State Graph - LangGraph execution engine for multi-agent workflow automation
Manages the execution flow and state transitions in the agent system
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
import operator

# Import agents
from agents.supervisor_agent import SupervisorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.search_agent import SearchAgent
from agents.code_agent import CodeAgent
from agents.planning_agent import PlanningAgent
from agents.creative_agent import CreativeAgent
from agents.translation_agent import TranslationAgent

# Import tools
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls
from tools.search_tool import web_search
from tools.delegation_tool import analyze_task_for_delegation


class TodoItem(TypedDict):
    """Structure for a TODO item."""
    id: str
    task: str
    status: str  # 'pending', 'in_progress', 'completed'
    assigned_agent: Optional[str]
    result: Optional[Dict[str, Any]]
    result_file: Optional[str]


class AgentState(TypedDict):
    """State structure for the multi-agent workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    user_input: str
    current_agent: str
    task_analysis: Dict[str, Any]
    todos: List[TodoItem]
    current_todo_id: Optional[str]
    execution_plan: List[str]
    intermediate_results: Annotated[List[Dict[str, Any]], operator.add]
    final_response: str
    tools_used: int
    context: Dict[str, Any]
    next_action: str
    session_id: Optional[str]
    conversation_history: List[Dict[str, Any]]
    delegated_to: Optional[str]
    iteration_count: int
    max_iterations: int


class MultiAgentWorkflow:
    """
    Multi-agent workflow orchestrator using LangGraph.
    Manages the execution flow between supervisor and specialized agents.
    """
    
    def __init__(self):
        """Initialize the multi-agent workflow."""
        # Initialize agents
        self.supervisor = SupervisorAgent()
        self.summarizer = SummarizerAgent()
        self.search_agent = SearchAgent()
        self.code_agent = CodeAgent()
        self.planning_agent = PlanningAgent()
        self.creative_agent = CreativeAgent()
        self.translation_agent = TranslationAgent()
        
        # Initialize tools
        self.tools = [
            vfs_write_file,
            vfs_read_file,
            vfs_ls,
            web_search
        ]
        
        self.tool_node = ToolNode(self.tools)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _tools_wrapper_node(self, state: AgentState) -> AgentState:
        """Wrapper for direct execution when no agent delegation matches."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                state["next_action"] = "continue"
                return state
            
            # Actually execute the task using the supervisor's LLM directly
            task = current_todo["task"]
            print(f"[DirectExecution] Processing: {task[:60]}...")
            
            response = self.supervisor.chain.invoke({"input": task})
            
            # Store the real result
            current_todo["status"] = "completed"
            current_todo["result"] = {
                "success": True,
                "result": response,
                "agent": "DirectExecution"
            }
            
            # Save to VFS
            result_file = f"result_{current_todo_id}.txt"
            vfs_write_file.invoke({"filename": result_file, "content": response})
            current_todo["result_file"] = result_file
            
            state["tools_used"] += 1
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "DirectExecution",
                "result": {"result": response},
                "timestamp": datetime.now().isoformat()
            })
            state["messages"].append(AIMessage(
                content=f"TODO {current_todo_id} completed via direct execution"
            ))
            
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Direct execution error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
                current_todo["result"] = {"success": False, "error": str(e)}
            state["next_action"] = "continue"
            return state
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with TODO-based execution loop."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)  # Creates TODOs
        workflow.add_node("executor", self._executor_node)  # Executes current TODO
        workflow.add_node("delegate_summarizer", self._summarizer_node)
        workflow.add_node("delegate_search", self._search_node)
        workflow.add_node("delegate_code", self._code_node)
        workflow.add_node("delegate_planning", self._planning_node)
        workflow.add_node("delegate_creative", self._creative_node)
        workflow.add_node("delegate_translation", self._translation_node)
        workflow.add_node("synthesizer", self._synthesizer_node)  # Final synthesis
        workflow.add_node("tools", self._tools_wrapper_node)
        
        # Define the workflow edges
        workflow.add_edge(START, "planner")
        
        # Planner creates TODOs, then goes to executor
        workflow.add_edge("planner", "executor")
        
        # Executor decides next action based on current TODO
        workflow.add_conditional_edges(
            "executor",
            self._route_executor,
            {
                "delegate_summarizer": "delegate_summarizer",
                "delegate_search": "delegate_search",
                "delegate_code": "delegate_code",
                "delegate_planning": "delegate_planning",
                "delegate_creative": "delegate_creative",
                "delegate_translation": "delegate_translation",
                "tools": "tools",
                "continue": "executor",  # Loop back for next TODO
                "synthesize": "synthesizer"
            }
        )
        
        # All specialized agents loop back to executor for next TODO
        workflow.add_edge("delegate_summarizer", "executor")
        workflow.add_edge("delegate_search", "executor")
        workflow.add_edge("delegate_code", "executor")
        workflow.add_edge("delegate_planning", "executor")
        workflow.add_edge("delegate_creative", "executor")
        workflow.add_edge("delegate_translation", "executor")
        workflow.add_edge("tools", "executor")
        
        # Synthesizer ends the workflow
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Planner node - analyzes request and creates TODO list."""
        try:
            # Initialize state with session-specific data
            if not state.get("messages"):
                state["messages"] = [HumanMessage(content=state["user_input"])]
                state["tools_used"] = 0
                state["intermediate_results"] = []
                state["context"] = {}
                state["delegated_to"] = None
                state["iteration_count"] = 0
                state["max_iterations"] = 10
            
            state["current_agent"] = "planner"
            
            # Get session ID for file isolation
            session_id = state.get("session_id", "default")
            
            # Analyze task complexity
            task_lower = state["user_input"].lower()
            
            # Determine if task needs breakdown into TODOs
            complex_indicators = [
                "plan", "create", "build", "develop", "design", "analyze and",
                "research and", "multiple", "step by step", "comprehensive"
            ]
            
            is_complex = any(indicator in task_lower for indicator in complex_indicators)
            word_count = len(state["user_input"].split())
            
            if is_complex or word_count > 20:
                # Create TODOs for complex task
                todos = self._create_todos(state["user_input"], session_id)
                state["todos"] = todos
                state["next_action"] = "execute"
                
                state["messages"].append(AIMessage(
                    content=f"Created {len(todos)} TODO items for execution"
                ))
            else:
                # Simple task - create single TODO
                todo_id = f"todo_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                state["todos"] = [{
                    "id": todo_id,
                    "task": state["user_input"],
                    "status": "pending",
                    "assigned_agent": None,
                    "result": None,
                    "result_file": None
                }]
                state["next_action"] = "execute"
            
            return state
            
        except Exception as e:
            state["next_action"] = "synthesize"
            state["final_response"] = f"Planning error: {str(e)}"
            state["messages"].append(AIMessage(content=f"Error: {str(e)}"))
            return state
    
    def _create_todos(self, user_input: str, session_id: str) -> List[TodoItem]:
        """Create TODO items from user request with session isolation."""
        # Use LLM to break down complex task
        prompt = f"""Break down this complex task into 3-5 specific sub-tasks:

Task: {user_input}

Return ONLY a numbered list of sub-tasks, one per line. Be specific and actionable.
Example format:
1. Research topic X
2. Analyze data Y
3. Create summary Z"""

        try:
            response = self.supervisor.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse numbered list
            lines = content.strip().split('\n')
            todos = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    task = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('- ')
                    if task:
                        todo_id = f"todo_{session_id}_{len(todos)+1}_{datetime.now().strftime('%H%M%S')}"
                        todos.append({
                            "id": todo_id,
                            "task": task,
                            "status": "pending",
                            "assigned_agent": None,
                            "result": None,
                            "result_file": None
                        })
            
            # Ensure at least one TODO
            if not todos:
                todo_id = f"todo_{session_id}_1_{datetime.now().strftime('%H%M%S')}"
                todos.append({
                    "id": todo_id,
                    "task": user_input,
                    "status": "pending",
                    "assigned_agent": None,
                    "result": None,
                    "result_file": None
                })
            
            return todos[:5]  # Limit to 5 TODOs
            
        except Exception as e:
            # Fallback: single TODO
            todo_id = f"todo_{session_id}_1_{datetime.now().strftime('%H%M%S')}"
            return [{
                "id": todo_id,
                "task": user_input,
                "status": "pending",
                "assigned_agent": None,
                "result": None,
                "result_file": None
            }]
    
    def _executor_node(self, state: AgentState) -> AgentState:
        """Executor node - processes current TODO and decides next action."""
        try:
            state["current_agent"] = "executor"
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            
            # Check iteration limit
            if state["iteration_count"] > state.get("max_iterations", 10):
                state["next_action"] = "synthesize"
                return state
            
            # Get next pending TODO
            todos = state.get("todos", [])
            pending_todos = [t for t in todos if t["status"] == "pending"]
            
            if not pending_todos:
                # All TODOs complete - synthesize
                state["next_action"] = "synthesize"
                return state
            
            # Select next TODO
            current_todo = pending_todos[0]
            current_todo["status"] = "in_progress"
            state["current_todo_id"] = current_todo["id"]
            
            # Analyze TODO for delegation
            delegation_analysis = analyze_task_for_delegation(current_todo["task"])
            recommended_agent = delegation_analysis.get("recommended_agent", "")
            confidence = delegation_analysis.get("confidence", 0)
            
            # Debug logging
            print(f"\n{'='*60}")
            print(f"DEBUG - Executor Node")
            print(f"{'='*60}")
            print(f"TODO: {current_todo['task'][:80]}")
            print(f"Recommended Agent: {recommended_agent}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Reasoning: {delegation_analysis.get('reasoning', 'N/A')}")
            
            # Decide action based on analysis (lowered threshold to 0.2 for better delegation)
            if confidence >= 0.2 and recommended_agent:
                # Delegate to specialist
                current_todo["assigned_agent"] = recommended_agent
                state["delegated_to"] = recommended_agent  # Track in state for visibility
                
                print(f"DELEGATING to {recommended_agent}")
                print(f"{'='*60}\n")
                
                if recommended_agent == "SummarizerAgent":
                    state["next_action"] = "delegate_summarizer"
                elif recommended_agent == "SearchAgent":
                    state["next_action"] = "delegate_search"
                elif recommended_agent == "CodeAgent":
                    state["next_action"] = "delegate_code"
                elif recommended_agent == "PlanningAgent":
                    state["next_action"] = "delegate_planning"
                elif recommended_agent == "CreativeAgent":
                    state["next_action"] = "delegate_creative"
                elif recommended_agent == "TranslationAgent":
                    state["next_action"] = "delegate_translation"
                else:
                    state["next_action"] = "tools"
            else:
                # Use tools or direct execution
                print(f"NO DELEGATION (confidence {confidence:.2f} <= 0.2)")
                print(f"{'='*60}\n")
                current_todo["assigned_agent"] = "DirectExecution"  # Mark as direct
                state["next_action"] = "tools"
            
            state["messages"].append(AIMessage(
                content=f"Executing TODO {current_todo['id']}: {current_todo['task'][:50]}... → Assigned to: {current_todo.get('assigned_agent', 'Tools')}"
            ))
            
            return state
            
        except Exception as e:
            state["next_action"] = "synthesize"
            state["messages"].append(AIMessage(content=f"Executor error: {str(e)}"))
            return state
    
    def _route_executor(self, state: AgentState) -> str:
        """Route from executor based on next action."""
        return state.get("next_action", "synthesize")
    
    def _summarizer_node(self, state: AgentState) -> AgentState:
        """Summarizer agent node."""
        try:
            # Get current TODO
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.summarizer.process_task(current_todo["task"], "")
            
            state["tools_used"] += 1
            state["current_agent"] = "summarizer"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("summary", "")
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            # Mark TODO as complete
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "SummarizerAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(
                content=f"TODO {current_todo_id} completed by Summarizer"
            ))
            
            # Continue to next TODO
            state["next_action"] = "continue"
            
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Summarizer error: {str(e)}"))
            # Mark TODO as completed even with error
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _search_node(self, state: AgentState) -> AgentState:
        """Search agent node."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.search_agent.process_task(current_todo["task"])
            
            state["tools_used"] += 1
            state["current_agent"] = "search"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("research_results", "")
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "SearchAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(
                content=f"TODO {current_todo_id} completed by Search"
            ))
            
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Search error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _code_node(self, state: AgentState) -> AgentState:
        """Code agent node."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.code_agent.process_task(current_todo["task"], "")
            
            state["tools_used"] += 1
            state["current_agent"] = "code"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("code_solution", "")
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "CodeAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(content=f"TODO {current_todo_id} completed by Code"))
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Code error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _planning_node(self, state: AgentState) -> AgentState:
        """Planning agent node."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.planning_agent.process_task(current_todo["task"], "")
            
            state["tools_used"] += 1
            state["current_agent"] = "planning"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("project_plan", result.get("strategy", ""))
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "PlanningAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(content=f"TODO {current_todo_id} completed by Planning"))
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Planning error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _creative_node(self, state: AgentState) -> AgentState:
        """Creative agent node."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.creative_agent.process_task(current_todo["task"], "")
            
            state["tools_used"] += 1
            state["current_agent"] = "creative"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("creative_content", result.get("blog_post", ""))
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "CreativeAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(content=f"TODO {current_todo_id} completed by Creative"))
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Creative error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _translation_node(self, state: AgentState) -> AgentState:
        """Translation agent node."""
        try:
            current_todo_id = state.get("current_todo_id")
            todos = state.get("todos", [])
            current_todo = next((t for t in todos if t["id"] == current_todo_id), None)
            
            if not current_todo:
                return state
            
            result = self.translation_agent.process_task(current_todo["task"], "")
            
            state["tools_used"] += 1
            state["current_agent"] = "translation"
            
            # Save result to file
            result_file = f"result_{current_todo_id}.txt"
            if result.get("success"):
                content = result.get("translation", "")
                vfs_write_file.invoke({"filename": result_file, "content": content})
                current_todo["result_file"] = result_file
            
            current_todo["status"] = "completed"
            current_todo["result"] = result
            
            state["intermediate_results"].append({
                "todo_id": current_todo_id,
                "agent": "TranslationAgent",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            state["messages"].append(AIMessage(content=f"TODO {current_todo_id} completed by Translation"))
            state["next_action"] = "continue"
            return state
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Translation error: {str(e)}"))
            if current_todo:
                current_todo["status"] = "completed"
            state["next_action"] = "continue"
            return state
    
    def _synthesizer_node(self, state: AgentState) -> AgentState:
        """Final synthesis node - reads all results from files and creates final output."""
        try:
            todos = state.get("todos", [])
            session_id = state.get("session_id", "default")
            conversation_history = state.get("conversation_history", [])
            
            # Gather all results from files
            all_results = []
            for todo in todos:
                if todo.get("result_file"):
                    # Read result from file
                    file_result = vfs_read_file.invoke({"filename": todo["result_file"]})
                    if file_result.get("success"):
                        all_results.append({
                            "todo": todo["task"],
                            "agent": todo.get("assigned_agent", "Unknown"),
                            "content": file_result.get("content", "")
                        })
                elif todo.get("result"):
                    # Use in-memory result
                    result = todo["result"]
                    content = self._extract_response_from_result(result, todo.get("assigned_agent", ""))
                    all_results.append({
                        "todo": todo["task"],
                        "agent": todo.get("assigned_agent", "Unknown"),
                        "content": content
                    })
            
            # Build conversation context (only from THIS session)
            context = ""
            if conversation_history:
                # Only use recent history from current session
                recent = conversation_history[-4:]  # Last 4 messages only
                context_parts = []
                for msg in recent:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:200]  # Limit length
                    if role == 'user':
                        context_parts.append(f"Previous question: {content}")
                context = "\n".join(context_parts) if context_parts else ""
            
            # If we have multiple results, synthesize them
            if len(all_results) > 1:
                synthesis_prompt = f"""Create a comprehensive response for this NEW request: {state['user_input']}

{f"Recent conversation context (for reference only):{context}" if context else ""}

Sub-task results to synthesize:
"""
                for i, result in enumerate(all_results, 1):
                    synthesis_prompt += f"\n{i}. {result['todo']}:\n{result['content'][:500]}...\n"
                
                synthesis_prompt += "\n\nIMPORTANT: Provide a well-structured, comprehensive response that ONLY addresses the current request. Do NOT reference or answer previous questions from the conversation history."
                
                final_response = self.supervisor.chain.invoke({"input": synthesis_prompt})
                state["final_response"] = final_response
                
            elif len(all_results) == 1:
                # Single result - use directly
                state["final_response"] = all_results[0]["content"]
                
            else:
                # No results - direct response with proper context isolation
                if context:
                    prompt = f"""Recent conversation (for context only):
{context}

NEW REQUEST: {state['user_input']}

Provide a helpful response to the NEW REQUEST above. Do NOT answer previous questions."""
                else:
                    prompt = state["user_input"]
                
                result = self.supervisor.execute_task_with_context(
                    prompt,
                    ""  # Empty context to avoid mixing
                )
                
                state["final_response"] = result.get("response", "Task completed.")
                state["tools_used"] += result.get("tools_used", 0)
            
            state["current_agent"] = "synthesizer"
            state["next_action"] = "end"
            
            # Add summary message
            completed_count = len([t for t in todos if t["status"] == "completed"])
            state["messages"].append(AIMessage(
                content=f"Synthesis complete. Processed {completed_count} TODOs for session {session_id}."
            ))
            
            # Clean up session-specific files to prevent leakage
            self._cleanup_session_files(session_id, todos)
            
            return state
            
        except Exception as e:
            state["final_response"] = f"I encountered an error during synthesis: {str(e)}"
            state["next_action"] = "end"
            state["messages"].append(AIMessage(content=f"Synthesis error: {str(e)}"))
            return state
    
    def _cleanup_session_files(self, session_id: str, todos: List[TodoItem]):
        """Clean up temporary result files for this session."""
        try:
            for todo in todos:
                if todo.get("result_file"):
                    # Files are automatically managed by VFS, no explicit cleanup needed
                    pass
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    def _extract_response_from_result(self, result: Dict[str, Any], agent_name: str) -> str:
        """Extract the main response from an agent result."""
        response_keys = [
            "summary", "research_results", "code_solution", "project_plan",
            "strategy", "task_breakdown", "timeline", "analysis",
            "blog_post", "marketing_copy", "creative_content",
            "translation", "translated_document", "localized_content"
        ]
        
        for key in response_keys:
            if key in result and isinstance(result[key], str) and len(result[key]) > 50:
                return result[key]
        
        return result.get("result", "")
    
    
    def run(self, user_input: str, conversation_history: List[Dict[str, Any]] = None, session_id: str = None) -> Dict[str, Any]:
        """Run the TODO-based multi-agent workflow with LangGraph."""
        from langsmith import traceable
        from langsmith import Client
        
        @traceable(
            run_type="chain",
            name="LangGraph TODO Workflow",
            metadata={
                "user_input": user_input[:200],
                "session_id": session_id,
                "has_history": bool(conversation_history)
            },
            tags=["langgraph", "todo_workflow"]
        )
        def execute_workflow():
            try:
                # Initialize state
                initial_state = {
                    "messages": [],
                    "user_input": user_input,
                    "current_agent": "",
                    "task_analysis": {},
                    "todos": [],
                    "current_todo_id": None,
                    "execution_plan": [],
                    "intermediate_results": [],
                    "final_response": "",
                    "tools_used": 0,
                    "context": {},
                    "next_action": "",
                    "session_id": session_id,
                    "conversation_history": conversation_history or [],
                    "delegated_to": None,
                    "iteration_count": 0,
                    "max_iterations": 10
                }
                
                # Execute workflow
                final_state = self.workflow.invoke(initial_state)
                
                # Extract TODO summary
                todos = final_state.get("todos", [])
                completed_todos = [t for t in todos if t["status"] == "completed"]
                
                # Debug: Print TODO details
                print(f"\nDEBUG - Workflow Complete:")
                print(f"  Total TODOs: {len(todos)}")
                print(f"  Completed TODOs: {len(completed_todos)}")
                for i, todo in enumerate(completed_todos, 1):
                    print(f"  TODO {i}: {todo.get('task', 'N/A')[:50]}")
                    print(f"    Assigned Agent: {todo.get('assigned_agent', 'None')}")
                
                # Collect all agents used
                agents_used = []
                for todo in completed_todos:
                    agent = todo.get("assigned_agent")
                    if agent and agent not in agents_used and agent != "DirectExecution":
                        agents_used.append(agent)
                
                # Format delegated_to as comma-separated list or single agent
                delegated_to = ", ".join(agents_used) if agents_used else "No sub-agents (direct execution)"
                
                print(f"  Agents Used: {agents_used}")
                print(f"  Delegated To: {delegated_to}\n")
                
                result = {
                    "success": True,
                    "final_response": final_state.get("final_response", "Task completed."),
                    "tools_used": final_state.get("tools_used", 0),
                    "todos_created": len(todos),
                    "todos_completed": len(completed_todos),
                    "execution_plan": [t["task"] for t in todos],
                    "intermediate_results": final_state.get("intermediate_results", []),
                    "delegated_to": delegated_to,  # All agents used
                    "agents_used": agents_used,  # List of agents
                    "workflow": "langgraph_todo",
                    "session_id": session_id,
                    "iterations": final_state.get("iteration_count", 0),
                    "state": final_state  # Include full state for debugging
                }
                
                # Try to update LangSmith trace with delegated_to info
                try:
                    from langsmith import get_current_run_tree
                    run_tree = get_current_run_tree()
                    if run_tree:
                        # Update the run name to include delegated agents
                        if agents_used:
                            run_tree.name = f"LangGraph TODO Workflow - Delegated to {delegated_to}"
                        run_tree.extra = run_tree.extra or {}
                        run_tree.extra["metadata"] = run_tree.extra.get("metadata", {})
                        run_tree.extra["metadata"]["delegated_to"] = delegated_to
                        run_tree.extra["metadata"]["agents_used"] = agents_used
                except Exception as e:
                    print(f"  Warning: Could not update LangSmith metadata: {e}")
                
                return result
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"LangGraph workflow error: {error_details}")
                return {
                    "success": False,
                    "error": str(e),
                    "final_response": f"Workflow error: {str(e)}",
                    "tools_used": 0,
                    "workflow": "langgraph_todo"
                }
        
        return execute_workflow()