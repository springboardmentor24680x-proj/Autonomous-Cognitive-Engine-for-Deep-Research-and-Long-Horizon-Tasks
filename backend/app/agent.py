import json
from datetime import datetime, timedelta
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from .utils import AgentState, get_or_create_session, parse_relative_date, call_gemini, format_message_history, sessions
from .tools import ToolExecutor

# ═══════════════════════════════════════════════════════════════════════════════
# LLM REASONING ENGINE - FIXED WITH NARRATION LAYER
# ═══════════════════════════════════════════════════════════════════════════════
#  FIX 3: Updated system prompt with strict narration rules
PLANNING_PROMPT = """You are an autonomous AI agent that helps users manage tasks, schedule events, and organize information.
## YOUR CAPABILITIES
You can execute these tools by returning JSON tool calls:
1. **create_todo** - Create a single task
   Parameters: title (required), description, priority (low/medium/high), due_date
2. **create_multiple_todos** - Create multiple tasks at once (use for trip planning, project breakdown, etc.)
   Parameters: todos_list (array of todo objects with title, description, priority, due_date)
3. **update_todo** - Modify an existing task
   Parameters: todo_id OR title_match, updates (object with fields to update)
4. **complete_todo** - Mark task as done
   Parameters: todo_id OR title_match
5. **delete_todo** - Remove a task
   Parameters: todo_id OR title_match
6. **create_calendar_event** - Schedule a meeting/event
   Parameters: title (required), date (required, YYYY-MM-DD), time (required, HH:MM 24hr format), duration_minutes, attendees (array), description
7. **update_calendar_event** - Modify an event
   Parameters: event_id OR title_match (omit both to use last meeting), updates object
   Use "add_attendees": ["name1", "name2"] to ADD people to existing attendees
8. **delete_calendar_event** - Cancel an event
   Parameters: event_id OR title_match
9. **save_file** - Save text content to a file
   Parameters: filename (required), content (required)
10. **read_file** - Read a file's content
    Parameters: filename (required)
11. **export_todos_to_file** - Export all tasks to a formatted file
    Parameters: filename (default: tasks.txt)
## CONTEXT AWARENESS
- "there" → refers to last_location: {last_location}
- "the meeting" / "it" (for events) → last_meeting_id: {last_meeting_id}
- "tomorrow" → {tomorrow_date}
- "today" → {today_date}
- "all my tasks" → current todos list
## RESPONSE FORMAT
Respond with valid JSON only:
{{
  "thinking": "Your reasoning about user intent",
  "tool_calls": [
    {{"tool": "tool_name", "parameters": {{...}}}}
  ]
}}
If no tools needed (informational question), use empty tool_calls array.
## IMPORTANT RULES
1. For trip planning: Create 5-7 SPECIFIC todos covering transport, accommodation, activities, packing
2. For meetings: Always include title, date (YYYY-MM-DD), time (HH:MM 24hr)
3. "invite X also" means ADD to existing attendees
4. Break complex requests into actionable items
## CURRENT STATE
Todos ({todo_count}): {todos}
Calendar ({event_count}): {calendar}
Files: {files}
"""
NARRATION_PROMPT = """You are a helpful AI assistant. Based on the tool execution results below, provide a clear, friendly response to the user.
## STRICT NARRATION RULES
1. **BE SPECIFIC**: Mention exact names, counts, priorities, dates, times
2. **USE FORMATTING**: Use emojis and markdown for clarity
3. **NEVER BE VAGUE**: Don't say "I've processed your request" or "Done"
4. **SUMMARIZE ACTIONS**: List exactly what was created/updated/deleted
5. **OFFER NEXT STEPS**: Suggest what the user might want to do next
## USER'S ORIGINAL REQUEST
{user_message}
## TOOL EXECUTION RESULTS
{tool_results}
## CURRENT STATE AFTER CHANGES
- Total todos: {todo_count}
- Total calendar events: {event_count}
- Files: {file_list}
## CONTEXT
- Last location discussed: {last_location}
- Last topic: {last_topic}
Now write a helpful, specific response. If tasks were created, list them by priority. If a meeting was scheduled, show all details. Be conversational but informative."""
DIRECT_RESPONSE_PROMPT = """You are a helpful AI assistant. Answer the user's question directly.
## USER'S QUESTION
{user_message}
## CONTEXT
- Last location discussed: {last_location}
- Last topic: {last_topic}
- Current todos: {todos}
- Current calendar: {calendar}
## RULES
1. If user asks "what's famous there?" - "there" refers to {last_location}
2. Be informative and helpful
3. Use formatting for readability
4. Offer to take actions if relevant
Respond naturally:"""

def get_planning_response(state: AgentState, user_message: str) -> dict:
    """Get tool calls from LLM - Planning phase"""
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
   
    prompt = PLANNING_PROMPT.format(
        last_location=state["context"].get("last_location", "None"),
        last_meeting_id=state["context"].get("last_meeting_id", "None"),
        today_date=today.strftime("%Y-%m-%d"),
        tomorrow_date=tomorrow.strftime("%Y-%m-%d"),
        todo_count=len(state["todos"]),
        todos=json.dumps(state["todos"][-5:], indent=2) if state["todos"] else "[]",
        event_count=len(state["calendar"]),
        calendar=json.dumps(state["calendar"][-3:], indent=2) if state["calendar"] else "[]",
        files=list(state["files"].keys()) if state["files"] else "[]"
    )
   
    full_prompt = f"""{prompt}
## CONVERSATION HISTORY (Last 5 messages)
{format_message_history(state["messages"][-10:])}
## CURRENT USER MESSAGE
{user_message}
Respond with JSON only. No markdown code blocks."""
    response_text = call_gemini(full_prompt)
   
    # Clean up response
    if response_text.startswith("```"):
        parts = response_text.split("```")
        response_text = parts[1] if len(parts) > 1 else response_text
        if response_text.startswith("json"):
            response_text = response_text[4:]
    response_text = response_text.strip()
   
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"thinking": "Could not parse", "tool_calls": []}

def get_narration_response(state: AgentState, user_message: str, tool_results: list) -> str:
    """Generate natural language response describing what was done - Narration phase"""
   
    if not tool_results:
        # No tools called - direct response needed
        prompt = DIRECT_RESPONSE_PROMPT.format(
            user_message=user_message,
            last_location=state["context"].get("last_location", "not specified"),
            last_topic=state["context"].get("last_topic", "general"),
            todos=json.dumps(state["todos"][-3:], indent=2) if state["todos"] else "None",
            calendar=json.dumps(state["calendar"][-2:], indent=2) if state["calendar"] else "None"
        )
        return call_gemini(prompt)
   
    # Tools were called - narrate the results
    prompt = NARRATION_PROMPT.format(
        user_message=user_message,
        tool_results=json.dumps(tool_results, indent=2),
        todo_count=len(state["todos"]),
        event_count=len(state["calendar"]),
        file_list=list(state["files"].keys()) if state["files"] else "None",
        last_location=state["context"].get("last_location", "not specified"),
        last_topic=state["context"].get("last_topic", "general")
    )
   
    return call_gemini(prompt)

def reasoning_node(state: AgentState) -> AgentState:
    """Main reasoning node - analyzes input, executes tools, generates response"""
   
    # Get the last user message
    last_message = state["messages"][-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
   
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Update context based on message content
    # ─────────────────────────────────────────────────────────────────────────
    location_keywords = ["manali", "goa", "delhi", "mumbai", "bangalore", "chennai",
                         "kolkata", "jaipur", "paris", "london", "tokyo", "new york",
                         "dubai", "singapore", "bali", "thailand", "maldives"]
    for loc in location_keywords:
        if loc in user_input.lower():
            state["context"]["last_location"] = loc.title()
            state["context"]["last_topic"] = f"trip to {loc.title()}"
            break
   
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Get LLM planning (tool selection)
    # ─────────────────────────────────────────────────────────────────────────
    llm_response = get_planning_response(state, user_input)
   
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Execute tools and collect results
    # ─────────────────────────────────────────────────────────────────────────
    tool_results = []
    executor = ToolExecutor()
   
    for tool_call in llm_response.get("tool_calls", []):
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
       
        # Handle date parsing for calendar events
        if tool_name == "create_calendar_event":
            if "date" in params:
                params["date"] = parse_relative_date(params["date"])
            # Ensure time is in correct format
            if "time" in params:
                time_str = params["time"]
                # Convert 12hr to 24hr if needed
                if "pm" in time_str.lower() or "am" in time_str.lower():
                    try:
                        time_obj = datetime.strptime(time_str, "%I:%M %p")
                        params["time"] = time_obj.strftime("%H:%M")
                    except:
                        try:
                            time_obj = datetime.strptime(time_str, "%I%p")
                            params["time"] = time_obj.strftime("%H:%M")
                        except:
                            pass
       
        # Execute the tool
        if hasattr(executor, tool_name):
            method = getattr(executor, tool_name)
            try:
                result = method(state, **params)
                tool_results.append(result)
            except Exception as e:
                tool_results.append({
                    "success": False,
                    "action": tool_name,
                    "summary": f"Error: {str(e)}"
                })
   
    # ─────────────────────────────────────────────────────────────────────────
    # ✅ FIX 2: Store tool results in context for potential follow-up
    # ─────────────────────────────────────────────────────────────────────────
    state["context"]["last_tool_results"] = tool_results
   
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Generate narration response (✅ FIX 3: Rich, specific response)
    # ─────────────────────────────────────────────────────────────────────────
    assistant_response = get_narration_response(state, user_input, tool_results)
   
    # ─────────────────────────────────────────────────────────────────────────
    # ✅ FIX 1: Add assistant message INSIDE the reasoning node
    # ─────────────────────────────────────────────────────────────────────────
    state["messages"].append(AIMessage(content=assistant_response))
   
    return state

def should_continue(state: AgentState) -> Literal["end"]:
    """Determine if agent should continue or end"""
    return "end"

# Build the graph
def create_agent_graph():
    """Create the LangGraph workflow"""
    workflow = StateGraph(AgentState)
   
    # Add nodes
    workflow.add_node("reasoning", reasoning_node)
   
    # Set entry point
    workflow.set_entry_point("reasoning")
   
    # Add edges
    workflow.add_conditional_edges(
        "reasoning",
        should_continue,
        {"end": END}
    )
   
    return workflow.compile()

# Create the agent
agent = create_agent_graph()