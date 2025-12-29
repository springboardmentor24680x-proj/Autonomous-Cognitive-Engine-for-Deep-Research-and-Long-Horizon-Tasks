#!/usr/bin/env python3
"""
State Graph - LangGraph execution engine for multi-agent workflow automation
Manages the execution flow and state transitions in the agent system
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

# Import agents
from agents.supervisor_agent import SupervisorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.search_agent import SearchAgent

# Import tools
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls, vfs_edit_file
from tools.search_tool import web_search


class AgentState(TypedDict):
    """State structure for the multi-agent workflow."""
    messages: List[BaseMessage]
    user_input: str
    current_agent: str
    task_analysis: Dict[str, Any]
    execution_plan: List[str]
    intermediate_results: List[Dict[str, Any]]
    final_response: str
    tools_used: int
    context: Dict[str, Any]
    next_action: str


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
        
        # Initialize tools
        self.tools = [
            vfs_write_file,
            vfs_read_file,
            vfs_ls,
            vfs_edit_file,
            web_search
        ]
        
        self.tool_executor = ToolExecutor(self.tools)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("summarizer", self._summarizer_node)
        workflow.add_node("search", self._search_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Define the workflow edges
        workflow.set_entry_point("supervisor")
        
        # Supervisor decides next action
        workflow.add_conditional_edges(
            "supervisor",
            self._route_supervisor,
            {
                "analyze": "analyzer",
                "plan": "planner",
                "execute": "executor",
                "delegate_summarize": "summarizer",
                "delegate_search": "search",
                "synthesize": "synthesizer",
                "end": END
            }
        )
        
        # Analyzer routes to planner
        workflow.add_edge("analyzer", "planner")
        
        # Planner routes to executor
        workflow.add_edge("planner", "executor")
        
        # Executor can route to specialized agents or synthesizer
        workflow.add_conditional_edges(
            "executor",
            self._route_executor,
            {
                "delegate_summarize": "summarizer",
                "delegate_search": "search",
                "synthesize": "synthesizer",
                "continue": "executor"
            }
        )
        
        # Specialized agents route back to synthesizer
        workflow.add_edge("summarizer", "synthesizer")
        workflow.add_edge("search", "synthesizer")
        
        # Synthesizer can end or continue
        workflow.add_conditional_edges(
            "synthesizer",
            self._route_synthesizer,
            {
                "end": END,
                "continue": "supervisor"
            }
        )
        
        return workflow.compile()
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor agent node - main orchestrator."""
        try:
            # Initialize if first run
            if not state.get("messages"):
                state["messages"] = [HumanMessage(content=state["user_input"])]
                state["current_agent"] = "supervisor"
                state["tools_used"] = 0
                state["intermediate_results"] = []
                state["context"] = {}
            
            # Supervisor analyzes and determines next action
            result = self.supervisor.analyze_task(state["user_input"])
            
            state["task_analysis"] = result
            state["current_agent"] = "supervisor"
            
            # Determine next action based on analysis
            if result.get("complexity") == "complex":
                state["next_action"] = "analyze"
            elif "summarize" in state["user_input"].lower():
                state["next_action"] = "delegate_summarize"
            elif "search" in state["user_input"].lower() or "research" in state["user_input"].lower():
                state["next_action"] = "delegate_search"
            else:
                state["next_action"] = "execute"
            
            return state
            
        except Exception as e:
            state["next_action"] = "end"
            state["final_response"] = f"Supervisor error: {str(e)}"
            return state
    
    def _analyzer_node(self, state: AgentState) -> AgentState:
        """Task analysis node."""
        try:
            # Perform detailed task analysis
            analysis = self.supervisor.analyze_task(state["user_input"])
            state["task_analysis"] = analysis
            state["current_agent"] = "analyzer"
            
            # Add analysis to intermediate results
            state["intermediate_results"].append({
                "step": "analysis",
                "result": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            return state
            
        except Exception as e:
            state["next_action"] = "end"
            state["final_response"] = f"Analysis error: {str(e)}"
            return state
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Task planning node."""
        try:
            # Create execution plan
            plan = self.supervisor.plan_execution(
                state["user_input"], 
                state.get("task_analysis", {})
            )
            
            state["execution_plan"] = plan
            state["current_agent"] = "planner"
            
            # Add plan to intermediate results
            state["intermediate_results"].append({
                "step": "planning",
                "result": {"plan": plan},
                "timestamp": datetime.now().isoformat()
            })
            
            return state
            
        except Exception as e:
            state["next_action"] = "end"
            state["final_response"] = f"Planning error: {str(e)}"
            return state
    
    def _executor_node(self, state: AgentState) -> AgentState:
        """Task execution node."""
        try:
            # Execute the main task
            result = self.supervisor.execute_task(state["user_input"])
            
            state["tools_used"] += result.get("tools_used", 0)
            state["current_agent"] = "executor"
            
            # Add execution result
            state["intermediate_results"].append({
                "step": "execution",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Determine if delegation is needed
            if "summarize" in result.get("response", "").lower():
                state["next_action"] = "delegate_summarize"
            elif "search" in result.get("response", "").lower():
                state["next_action"] = "delegate_search"
            else:
                state["next_action"] = "synthesize"
            
            return state
            
        except Exception as e:
            state["next_action"] = "synthesize"
            state["intermediate_results"].append({
                "step": "execution_error",
                "result": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            })
            return state
    
    def _summarizer_node(self, state: AgentState) -> AgentState:
        """Summarizer agent node."""
        try:
            # Use summarizer agent
            result = self.summarizer.process_task(
                state["user_input"],
                state.get("context", {}).get("content", "")
            )
            
            state["tools_used"] += 1
            state["current_agent"] = "summarizer"
            
            # Add summarization result
            state["intermediate_results"].append({
                "step": "summarization",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return state
            
        except Exception as e:
            state["intermediate_results"].append({
                "step": "summarization_error",
                "result": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            })
            return state
    
    def _search_node(self, state: AgentState) -> AgentState:
        """Search agent node."""
        try:
            # Use search agent
            result = self.search_agent.process_task(state["user_input"])
            
            state["tools_used"] += 1
            state["current_agent"] = "search"
            
            # Add search result
            state["intermediate_results"].append({
                "step": "search",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return state
            
        except Exception as e:
            state["intermediate_results"].append({
                "step": "search_error",
                "result": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            })
            return state
    
    def _synthesizer_node(self, state: AgentState) -> AgentState:
        """Final synthesis node."""
        try:
            # Synthesize all results into final response
            intermediate_results = state.get("intermediate_results", [])
            
            # Combine all results
            synthesis_content = []
            
            for result in intermediate_results:
                step = result.get("step", "unknown")
                data = result.get("result", {})
                
                if step == "execution" and data.get("success"):
                    synthesis_content.append(data.get("response", ""))
                elif step == "summarization" and data.get("success"):
                    synthesis_content.append(data.get("summary", ""))
                elif step == "search" and data.get("success"):
                    synthesis_content.append(data.get("research_results", ""))
            
            # Create final response
            if synthesis_content:
                final_response = "\n\n".join(synthesis_content)
            else:
                final_response = "Task completed successfully."
            
            state["final_response"] = final_response
            state["current_agent"] = "synthesizer"
            state["next_action"] = "end"
            
            return state
            
        except Exception as e:
            state["final_response"] = f"Synthesis error: {str(e)}"
            state["next_action"] = "end"
            return state
    
    def _route_supervisor(self, state: AgentState) -> str:
        """Route from supervisor based on next action."""
        return state.get("next_action", "end")
    
    def _route_executor(self, state: AgentState) -> str:
        """Route from executor based on next action."""
        return state.get("next_action", "synthesize")
    
    def _route_synthesizer(self, state: AgentState) -> str:
        """Route from synthesizer."""
        return state.get("next_action", "end")
    
    def run(self, user_input: str) -> Dict[str, Any]:
        """Run the multi-agent workflow."""
        try:
            # Initialize state
            initial_state = AgentState(
                messages=[],
                user_input=user_input,
                current_agent="",
                task_analysis={},
                execution_plan=[],
                intermediate_results=[],
                final_response="",
                tools_used=0,
                context={},
                next_action=""
            )
            
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "final_response": final_state.get("final_response", "Task completed."),
                "tools_used": final_state.get("tools_used", 0),
                "execution_plan": final_state.get("execution_plan", []),
                "intermediate_results": final_state.get("intermediate_results", []),
                "workflow": "multi_agent_langgraph"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_response": f"Workflow error: {str(e)}",
                "tools_used": 0
            }