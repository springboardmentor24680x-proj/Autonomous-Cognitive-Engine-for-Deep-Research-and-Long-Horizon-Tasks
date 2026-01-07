from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

from .utils import AgentState
from .tool_executor import ToolExecutor
from .sub_agents import SUB_AGENTS
import json
import re

load_dotenv()

# Initialize LLM for decision making
decision_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1024,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def reasoning_node(state: AgentState) -> AgentState:
    """
    Main reasoning node - decides what to do
    Now properly traced in LangSmith with sub-agent delegation visible
    """
    
    messages = state["messages"]
    last_user_msg = messages[-1].content if messages else ""
    
    # Build context about current state
    context_summary = f"""
Current State:
- Tasks: {len(state['todos'])} total ({len([t for t in state['todos'] if not t['completed']])} pending)
- Calendar: {len(state['calendar'])} events
- Files: {len(state['files'])} files
- Visualizations: {len(state['visualizations'])}

Recent conversation:
{_format_recent_messages(messages[-6:])}
"""

    # Decision prompt
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a decision-making AI that routes requests to the appropriate handler.

{context}

You have THREE options:

1. **EXECUTE TOOL** - For direct CRUD operations
   Tools: create_todo, create_multiple_todos, complete_todo, update_todo, delete_todo,
   create_calendar_event, update_calendar_event, delete_calendar_event,
   save_file, read_file, delete_file, ls, export_todos_to_file

2. **DELEGATE TO SUB-AGENT** - For specialized tasks
   Agents:
   - web_search: Research and information gathering
   - summarizer: Condense content
   - analyzer: Deep analysis with charts
   - visualizer: Create charts from task data
   - report_generator: Professional reports
   - planning: Strategic planning

3. **RESPOND DIRECTLY** - For simple queries

Respond ONLY with valid JSON:
{{
  "action": "tool" | "delegate" | "respond",
  "tool_name": "tool_name" (if action=tool),
  "tool_params": {{...}} (if action=tool),
  "agent_name": "agent_name" (if action=delegate),
  "response": "message" (if action=respond),
  "reasoning": "explanation"
}}"""),
        ("human", "{user_request}")
    ])
    
    # Create decision chain
    decision_chain = (
        decision_prompt 
        | decision_llm
        | RunnableLambda(_parse_decision)
    ).with_config({"run_name": "decision_making"})
    
    # Get decision
    try:
        decision = decision_chain.invoke({
            "context": context_summary,
            "user_request": last_user_msg
        })
        
        action = decision.get("action", "respond")
        
        print(f"\n DECISION: {action}")
        print(f" REASONING: {decision.get('reasoning', 'N/A')}")
        
        if action == "tool":
            return _execute_tool_action(state, decision)
        
        elif action == "delegate":
            return _execute_delegation(state, decision, last_user_msg)
        
        else:
            # Direct response
            response = decision.get("response", "I'm here to help!")
            state["messages"].append(AIMessage(content=response))
            return state
            
    except Exception as e:
        print(f" Decision error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback
        state["messages"].append(AIMessage(content="I encountered an error processing your request. Please try again."))
        return state


def _parse_decision(llm_output) -> dict:
    """Parse LLM decision output"""
    text = llm_output.content if hasattr(llm_output, 'content') else str(llm_output)
    
    # Extract JSON
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    
    # Fallback
    return {"action": "respond", "response": "I'm not sure how to help with that.", "reasoning": "Could not parse decision"}


def _execute_tool_action(state: AgentState, decision: dict) -> AgentState:
    """Execute a tool directly - traced as tool execution"""
    tool_name = decision.get("tool_name")
    params = decision.get("tool_params", {})
    
    print(f" EXECUTING TOOL: {tool_name}")
    print(f"PARAMS: {params}")
    
    def tool_executor_wrapper(inputs):
        """Wrapper for tool execution to make it traceable"""
        state = inputs["state"]
        tool_name = inputs["tool_name"]
        params = inputs["params"]
        
        tool_method = getattr(ToolExecutor, tool_name, None)
        if not tool_method:
            return {"success": False, "summary": f"Unknown tool: {tool_name}"}
        
        return tool_method(state, **params)
    
    # Create traceable tool execution
    tool_chain = RunnableLambda(tool_executor_wrapper).with_config({"run_name": f"Tool_{tool_name}"})
    
    try:
        result = tool_chain.invoke({
            "state": state,
            "tool_name": tool_name,
            "params": params
        })
        
        # Format response
        if result.get("success"):
            response = result.get("summary", "Done!")
            if "visualizations" in result:
                response += "\n\n Visualization created!"
        else:
            response = f"{result.get('summary', 'Operation failed')}"
        
        state["messages"].append(AIMessage(content=response))
        
    except Exception as e:
        print(f" Tool execution error: {e}")
        state["messages"].append(AIMessage(content=f" Error: {str(e)}"))
    
    return state


def _execute_delegation(state: AgentState, decision: dict, user_request: str) -> AgentState:
    """
    Delegate to a sub-agent
    THIS WILL NOW BE VISIBLE IN LANGSMITH as separate agent execution
    """
    agent_name = decision.get("agent_name", "").lower()
    
    if agent_name not in SUB_AGENTS:
        state["messages"].append(AIMessage(content=f" Unknown agent: {agent_name}"))
        return state
    
    print(f" DELEGATING TO: {agent_name}")
    
    # Get the sub-agent (it's now a RunnableLambda, so it will be traced)
    sub_agent = SUB_AGENTS[agent_name]["agent"]
    
    # Prepare input
    sub_agent_input = {
        "messages": [{"role": "user", "content": user_request}],
        "state": state
    }
    
    try:
        # Invoke sub-agent (this creates a trace in LangSmith)
        result = sub_agent.invoke(sub_agent_input)
        
        # Extract response
        response_content = result.get("messages", [{}])[0].get("content", "No response from agent")
        
        # Handle render components (charts)
        render_components = result.get("render_components", [])
        if render_components:
            print(f" VISUALIZATIONS CREATED: {len(render_components)}")
            state["visualizations"].extend(render_components)
            response_content += f"\n\n {len(render_components)} visualization(s) created!"
        
        state["messages"].append(AIMessage(content=response_content))
        
    except Exception as e:
        print(f" Sub-agent error: {e}")
        import traceback
        traceback.print_exc()
        state["messages"].append(AIMessage(content=f" Agent error: {str(e)}"))
    
    return state


def _format_recent_messages(messages) -> str:
    """Format recent messages for context"""
    lines = []
    for msg in messages[-4:]:
        role = "User" if msg.type == "human" else "Assistant"
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


# Build the graph
workflow = StateGraph(AgentState)

# Wrap reasoning node to make it traceable
reasoning_runnable = RunnableLambda(reasoning_node).with_config({"run_name": "reasoning"})

workflow.add_node("reasoning", reasoning_runnable)
workflow.set_entry_point("reasoning")
workflow.add_edge("reasoning", END)

agent = workflow.compile()