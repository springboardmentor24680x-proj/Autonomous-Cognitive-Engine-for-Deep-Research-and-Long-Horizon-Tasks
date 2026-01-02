import json
import re
from datetime import datetime, timedelta
from typing import Literal

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage

from .utils import (
    AgentState,
    parse_relative_date,
    call_gemini,
    format_message_history,
)
from .tools import ToolExecutor
from .sub_agents import SUB_AGENTS


# =========================================================
# ENHANCED PLANNING PROMPT
# =========================================================

PLANNING_PROMPT = """
You are an autonomous AI agent that plans and executes tasks.

You MUST respond with VALID JSON only. No extra text before or after.

## CURRENT STATE
Todos: {todos}
Calendar: {calendar}
Files: {files}

## AVAILABLE TOOLS

### Task Management
- create_todo(title, description?, priority?, due_date?) - Create a single task
- create_multiple_todos(todos_list) - Create multiple tasks at once
  Format: [{{"title": "...", "description": "...", "priority": "high/medium/low", "due_date": "YYYY-MM-DD"}}]
- update_todo(todo_id?, title_match?, updates) - Update a task
- complete_todo(todo_id?, title_match?) - Mark task as complete
- delete_todo(todo_id?, title_match?) - Delete a task

### Calendar Management
- create_calendar_event(title, date, time, duration_minutes?, attendees?, description?)
  Format: date="YYYY-MM-DD", time="HH:MM"
- update_calendar_event(event_id?, title_match?, updates)
- delete_calendar_event(event_id?, title_match?)

### File Operations
- save_file(filename, content) - Save content to file
- read_file(filename) - Read file content
- export_todos_to_file(filename?) - Export all tasks to formatted file
- ls() - List all files

### Delegation (USE FOR RESEARCH/ANALYSIS)
- delegate_task(task, agent_name) - Delegate to specialized sub-agent

## AVAILABLE SUB-AGENTS
- web_search: Real-time web research and information gathering
- summarizer: Summarize content into concise bullet points
- analyzer: Deep analysis and insights
- report_generator: Create professional structured reports
- visualizer: Generate tables and charts from data

## DECISION RULES
1. For ANY research, information lookup, or "find out about" requests → delegate_task to web_search
2. For summarization requests → delegate_task to summarizer
3. For analysis requests → delegate_task to analyzer
4. For report creation → delegate_task to report_generator
5. For creating tasks/events/files → use direct tools
6. For visualization requests → delegate_task to visualizer

## RESPONSE FORMAT
{{
  "thinking": "Step by step reasoning about what to do",
  "tool_calls": [
    {{
      "tool": "tool_name",
      "parameters": {{"param": "value"}}
    }}
  ]
}}

## EXAMPLES

User: "Research the best hotels in Paris"
{{
  "thinking": "User wants research on Paris hotels. This requires web_search agent.",
  "tool_calls": [
    {{
      "tool": "delegate_task",
      "parameters": {{
        "task": "Find and list the top 5 best hotels in Paris with their ratings, locations, and key features",
        "agent_name": "web_search"
      }}
    }}
  ]
}}

User: "Create tasks for my Paris trip"
{{
  "thinking": "User wants to create multiple tasks. Use create_multiple_todos.",
  "tool_calls": [
    {{
      "tool": "create_multiple_todos",
      "parameters": {{
        "todos_list": [
          {{"title": "Book hotel in Paris", "priority": "high", "due_date": "2025-01-15"}},
          {{"title": "Book flight tickets", "priority": "high", "due_date": "2025-01-10"}},
          {{"title": "Create itinerary", "priority": "medium", "due_date": "2025-01-20"}}
        ]
      }}
    }}
  ]
}}

User: "Schedule a meeting with John tomorrow at 3pm"
{{
  "thinking": "Create calendar event for tomorrow at 3pm with John",
  "tool_calls": [
    {{
      "tool": "create_calendar_event",
      "parameters": {{
        "title": "Meeting with John",
        "date": "tomorrow",
        "time": "15:00",
        "duration_minutes": 60,
        "attendees": ["John"]
      }}
    }}
  ]
}}

CRITICAL: Always return valid JSON. Match tool names and parameters exactly as shown.
"""


# =========================================================
# JSON EXTRACTION (ROBUST)
# =========================================================

def extract_json(text: str) -> dict:
    """Extract and parse JSON from LLM response"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return {"thinking": "No JSON found in response", "tool_calls": []}
    
    try:
        parsed = json.loads(match.group())
        # Ensure required fields exist
        if "tool_calls" not in parsed:
            parsed["tool_calls"] = []
        if "thinking" not in parsed:
            parsed["thinking"] = ""
        return parsed
    except json.JSONDecodeError as e:
        return {"thinking": f"Invalid JSON: {str(e)}", "tool_calls": []}


# =========================================================
# TOOL PARAM NORMALIZER
# =========================================================

def normalize_tool_params(tool_name: str, params: dict) -> dict:
    """Normalize parameters to handle LLM variations"""
    
    if tool_name == "create_todo":
        return {
            "title": params.get("title") or params.get("task") or "",
            "description": params.get("description", ""),
            "priority": params.get("priority", "medium"),
            "due_date": parse_relative_date(params.get("due_date") or "")
        }

    if tool_name == "create_multiple_todos":
        todos_list = params.get("todos_list") or params.get("todos") or params.get("tasks") or []
        # Normalize each todo in the list
        normalized_list = []
        for todo in todos_list:
            normalized_list.append({
                "title": todo.get("title") or todo.get("task") or "Untitled",
                "description": todo.get("description", ""),
                "priority": todo.get("priority", "medium"),
                "due_date": parse_relative_date(todo.get("due_date") or "")
            })
        return {"todos_list": normalized_list}

    if tool_name == "complete_todo":
        return {
            "todo_id": params.get("todo_id"),
            "title_match": params.get("title") or params.get("task") or params.get("title_match")
        }

    if tool_name == "update_todo":
        return {
            "todo_id": params.get("todo_id"),
            "title_match": params.get("title") or params.get("title_match"),
            "updates": params.get("updates", {})
        }
    
    if tool_name == "delete_todo":
        return {
            "todo_id": params.get("todo_id"),
            "title_match": params.get("title") or params.get("task") or params.get("title_match")
        }

    if tool_name == "create_calendar_event":
        date = parse_relative_date(params.get("date") or "")
        time = params.get("time") or params.get("start_time") or "09:00"
        
        return {
            "title": params.get("title") or "Untitled Event",
            "date": date,
            "time": time,
            "duration_minutes": params.get("duration_minutes", 60),
            "attendees": params.get("attendees", []),
            "description": params.get("description", "")
        }
    
    if tool_name == "update_calendar_event":
        return {
            "event_id": params.get("event_id"),
            "title_match": params.get("title") or params.get("title_match"),
            "updates": params.get("updates", {})
        }
    
    if tool_name == "delete_calendar_event":
        return {
            "event_id": params.get("event_id"),
            "title_match": params.get("title") or params.get("title_match")
        }

    return params


# =========================================================
# PLANNING STEP
# =========================================================

def get_planning_response(state: AgentState, user_message: str) -> dict:
    """Get planning decision from LLM"""
    
    # Format current state concisely
    todos_summary = f"{len(state['todos'])} tasks ({sum(1 for t in state['todos'] if not t['completed'])} pending)"
    calendar_summary = f"{len(state['calendar'])} events"
    files_summary = f"{len(state['files'])} files: {', '.join(list(state['files'].keys())[:5])}"
    
    prompt = PLANNING_PROMPT.format(
        todos=todos_summary,
        calendar=calendar_summary,
        files=files_summary
    )

    # Include recent conversation context
    recent_messages = state["messages"][-6:] if len(state["messages"]) > 6 else state["messages"]
    conversation_context = format_message_history(recent_messages)

    full_prompt = f"""{prompt}

## RECENT CONVERSATION
{conversation_context}

## CURRENT USER REQUEST
{user_message}

Respond with JSON only:"""

    response = call_gemini(full_prompt)
    return extract_json(response)


# =========================================================
# NARRATION STEP
# =========================================================

def get_narration_response(state: AgentState, user_message: str, tool_results: list) -> str:
    """Generate natural language response based on tool results"""
    
    # Special handling for delegated tasks
    if state["context"].get("last_delegated_result"):
        delegated = state["context"]["last_delegated_result"]
        agent_name = delegated.get("agent", "sub-agent")
        result = delegated.get("result", "")
        
        # Clear the flag
        state["context"]["last_delegated_result"] = None
        
        return f"""✅ **{agent_name.replace('_', ' ').title()} Complete**

{result}

Would you like me to:
- Turn this into actionable tasks?
- Save this as a file?
- Create calendar events?
- Perform additional analysis?

Let me know how I can help! 😊"""

    # Handle regular tool results
    if not tool_results:
        return "I processed your request, but no actions were taken. Could you clarify what you'd like me to do?"

    # Build natural response from tool results
    successes = [r for r in tool_results if r.get("success")]
    failures = [r for r in tool_results if not r.get("success")]
    
    response_parts = []
    
    if successes:
        response_parts.append("✅ **Completed:**")
        for result in successes:
            summary = result.get("summary", "Action completed")
            response_parts.append(f"- {summary}")
    
    if failures:
        response_parts.append("\n⚠️ **Issues:**")
        for result in failures:
            summary = result.get("summary", "Action failed")
            response_parts.append(f"- {summary}")
    
    # Add helpful context
    if any(r.get("action") == "created_todo" for r in successes):
        pending_count = sum(1 for t in state["todos"] if not t["completed"])
        response_parts.append(f"\n📋 You now have {pending_count} pending tasks.")
    
    if any(r.get("action") == "created_calendar_event" for r in successes):
        response_parts.append(f"\n📅 You have {len(state['calendar'])} events scheduled.")
    
    response_parts.append("\nWhat else can I help you with? 😊")
    
    return "\n".join(response_parts)


# =========================================================
# MAIN REASONING NODE
# =========================================================

def reasoning_node(state: AgentState) -> AgentState:
    """Main orchestration logic"""
    
    user_message = state["messages"][-1].content

    # Get plan from LLM
    plan = get_planning_response(state, user_message)
    state["context"]["last_thinking"] = plan.get("thinking", "")

    tool_results = []
    executor = ToolExecutor()

    # Execute each tool call
    for call in plan.get("tool_calls", []):
        tool_name = call.get("tool")
        params = call.get("parameters", {})

        # -----------------------------
        # DELEGATION (SPECIAL HANDLING)
        # -----------------------------
        if tool_name == "delegate_task":
            agent_name = params.get("agent_name")
            task = params.get("task")

            if not agent_name:
                tool_results.append({
                    "success": False,
                    "summary": "No agent name specified for delegation"
                })
                continue

            if agent_name not in SUB_AGENTS:
                available = ", ".join(SUB_AGENTS.keys())
                tool_results.append({
                    "success": False,
                    "summary": f"Unknown agent '{agent_name}'. Available: {available}"
                })
                continue

            try:
                # Get the sub-agent
                sub_agent_fn = SUB_AGENTS[agent_name]["agent"]
                
                # Invoke with proper context
                result = sub_agent_fn({
                    "messages": [{"role": "user", "content": task}],
                    "state": state  # Pass state for read-only access
                })

                content = result["messages"][-1]["content"]
                
                # Store for narration
                state["context"]["last_delegated_result"] = {
                    "agent": agent_name,
                    "result": content
                }

                tool_results.append({
                    "success": True,
                    "action": "delegate_task",
                    "agent": agent_name,
                    "result": content[:200] + "..." if len(content) > 200 else content,
                    "summary": f"Successfully delegated to {agent_name}"
                })
            except Exception as e:
                tool_results.append({
                    "success": False,
                    "summary": f"Delegation to {agent_name} failed: {str(e)}"
                })
            continue

        # -----------------------------
        # NORMAL TOOL EXECUTION
        # -----------------------------
        if hasattr(executor, tool_name):
            clean_params = normalize_tool_params(tool_name, params)
            try:
                result = getattr(executor, tool_name)(state, **clean_params)
                tool_results.append(result)
            except Exception as e:
                tool_results.append({
                    "success": False,
                    "summary": f"{tool_name} failed: {str(e)}"
                })
        else:
            tool_results.append({
                "success": False,
                "summary": f"Unknown tool: {tool_name}"
            })

    # Store results in context
    state["context"]["last_tool_results"] = tool_results

    # Generate natural language response
    reply = get_narration_response(state, user_message, tool_results)
    state["messages"].append(AIMessage(content=reply))

    return state


# =========================================================
# GRAPH
# =========================================================

def should_continue(_: AgentState) -> Literal["end"]:
    return "end"


def create_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("reasoning", reasoning_node)
    graph.set_entry_point("reasoning")
    graph.add_conditional_edges("reasoning", should_continue, {"end": END})
    return graph.compile()


agent = create_agent_graph()