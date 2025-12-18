# backend/main.py
"""
Autonomous AI Agent Backend - FIXED VERSION
Proper narration layer, tool result feedback, and message handling
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Annotated, TypedDict, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="Autonomous AI Agent", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """The complete state of the agent - persisted across turns"""
    messages: Annotated[list, add_messages]  # Conversation history (LangGraph managed)
    todos: list[dict]                         # Task list
    files: dict[str, str]                     # Saved files
    calendar: list[dict]                      # Calendar events
    context: dict                             # Contextual memory

# In-memory session storage (use Redis/DB in production)
sessions: dict[str, AgentState] = {}

def get_or_create_session(session_id: str) -> AgentState:
    """Get existing session or create new one"""
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "todos": [],
            "files": {},
            "calendar": [],
            "context": {
                "last_location": None,
                "last_meeting_id": None,
                "last_topic": None,
                "last_tool_results": [],  # ✅ FIX 2: Store tool results
                "user_preferences": {}
            }
        }
    return sessions[session_id]

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS (Same as before, but with richer return data)
# ═══════════════════════════════════════════════════════════════════════════════

class ToolExecutor:
    """Executes tools and updates state - returns rich data for narration"""
    
    @staticmethod
    def create_todo(state: AgentState, title: str, description: str = "", 
                    priority: str = "medium", due_date: str = None) -> dict:
        """Create a new todo item"""
        todo = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        state["todos"].append(todo)
        return {
            "success": True, 
            "action": "created_todo",
            "todo": todo, 
            "summary": f"Created task: '{title}' with {priority} priority"
        }
    
    @staticmethod
    def create_multiple_todos(state: AgentState, todos_list: list[dict]) -> dict:
        """Create multiple todos at once (for trip planning, etc.)"""
        created = []
        summaries = {"high": [], "medium": [], "low": []}
        
        for item in todos_list:
            priority = item.get("priority", "medium")
            todo = {
                "id": str(uuid.uuid4())[:8],
                "title": item.get("title", "Untitled"),
                "description": item.get("description", ""),
                "priority": priority,
                "due_date": item.get("due_date"),
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            state["todos"].append(todo)
            created.append(todo)
            summaries[priority].append(todo["title"])
        
        return {
            "success": True, 
            "action": "created_multiple_todos",
            "count": len(created),
            "todos": created,
            "by_priority": summaries,
            "summary": f"Created {len(created)} tasks"
        }
    
    @staticmethod
    def update_todo(state: AgentState, todo_id: str = None, title_match: str = None,
                    updates: dict = None) -> dict:
        """Update an existing todo by ID or title match"""
        for todo in state["todos"]:
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                old_title = todo["title"]
                if updates:
                    todo.update(updates)
                return {
                    "success": True, 
                    "action": "updated_todo",
                    "todo": todo, 
                    "summary": f"Updated task '{old_title}'"
                }
        return {"success": False, "action": "update_todo_failed", "summary": "Task not found"}
    
    @staticmethod
    def complete_todo(state: AgentState, todo_id: str = None, title_match: str = None) -> dict:
        """Mark a todo as completed"""
        for todo in state["todos"]:
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                todo["completed"] = True
                return {
                    "success": True, 
                    "action": "completed_todo",
                    "todo": todo, 
                    "summary": f"Completed: '{todo['title']}'"
                }
        return {"success": False, "action": "complete_todo_failed", "summary": "Task not found"}
    
    @staticmethod
    def delete_todo(state: AgentState, todo_id: str = None, title_match: str = None) -> dict:
        """Delete a todo"""
        for i, todo in enumerate(state["todos"]):
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                removed = state["todos"].pop(i)
                return {
                    "success": True, 
                    "action": "deleted_todo",
                    "summary": f"Deleted task: '{removed['title']}'"
                }
        return {"success": False, "action": "delete_todo_failed", "summary": "Task not found"}
    
    @staticmethod
    def create_calendar_event(state: AgentState, title: str, date: str, time: str,
                              duration_minutes: int = 60, attendees: list[str] = None,
                              description: str = "") -> dict:
        """Create a calendar event"""
        event = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "attendees": attendees or [],
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        state["calendar"].append(event)
        state["context"]["last_meeting_id"] = event["id"]
        
        # Format time for display
        try:
            time_obj = datetime.strptime(time, "%H:%M")
            formatted_time = time_obj.strftime("%I:%M %p")
        except:
            formatted_time = time
            
        # Format date for display
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = date
        
        return {
            "success": True, 
            "action": "created_calendar_event",
            "event": event,
            "formatted_date": formatted_date,
            "formatted_time": formatted_time,
            "summary": f"Scheduled '{title}' on {formatted_date} at {formatted_time}"
        }
    
    @staticmethod
    def update_calendar_event(state: AgentState, event_id: str = None, 
                              title_match: str = None, updates: dict = None) -> dict:
        """Update a calendar event"""
        # If no ID provided, use last meeting from context
        if not event_id and not title_match:
            event_id = state["context"].get("last_meeting_id")
        
        for event in state["calendar"]:
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                changes_made = []
                if updates:
                    # Handle attendee additions specially
                    if "add_attendees" in updates:
                        new_attendees = updates["add_attendees"]
                        event["attendees"] = list(set(event.get("attendees", []) + new_attendees))
                        changes_made.append(f"Added {', '.join(new_attendees)} to attendees")
                        del updates["add_attendees"]
                    
                    for key, value in updates.items():
                        event[key] = value
                        changes_made.append(f"Updated {key} to {value}")
                
                return {
                    "success": True, 
                    "action": "updated_calendar_event",
                    "event": event,
                    "changes": changes_made,
                    "summary": f"Updated '{event['title']}': {'; '.join(changes_made)}"
                }
        return {"success": False, "action": "update_event_failed", "summary": "Event not found"}
    
    @staticmethod
    def delete_calendar_event(state: AgentState, event_id: str = None, 
                              title_match: str = None) -> dict:
        """Delete a calendar event"""
        for i, event in enumerate(state["calendar"]):
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                removed = state["calendar"].pop(i)
                return {
                    "success": True, 
                    "action": "deleted_calendar_event",
                    "summary": f"Cancelled event: '{removed['title']}'"
                }
        return {"success": False, "action": "delete_event_failed", "summary": "Event not found"}
    
    @staticmethod
    def save_file(state: AgentState, filename: str, content: str) -> dict:
        """Save content to a file"""
        state["files"][filename] = content
        return {
            "success": True, 
            "action": "saved_file",
            "filename": filename,
            "size": len(content),
            "summary": f"Saved file: '{filename}' ({len(content)} characters)"
        }
    
    @staticmethod
    def read_file(state: AgentState, filename: str) -> dict:
        """Read a file's content"""
        if filename in state["files"]:
            content = state["files"][filename]
            return {
                "success": True, 
                "action": "read_file",
                "filename": filename, 
                "content": content,
                "summary": f"Read file: '{filename}'"
            }
        return {"success": False, "action": "read_file_failed", "summary": f"File not found: {filename}"}
    
    @staticmethod
    def delete_file(state: AgentState, filename: str) -> dict:
        """Delete a file"""
        if filename in state["files"]:
            del state["files"][filename]
            return {
                "success": True, 
                "action": "deleted_file",
                "summary": f"Deleted file: '{filename}'"
            }
        return {"success": False, "action": "delete_file_failed", "summary": f"File not found: {filename}"}
    
    @staticmethod
    def export_todos_to_file(state: AgentState, filename: str = "tasks.txt") -> dict:
        """Export all todos to a formatted file"""
        if not state["todos"]:
            return {"success": False, "action": "export_failed", "summary": "No tasks to export"}
        
        content_lines = ["=" * 50, "MY TASKS", "=" * 50, ""]
        
        completed_count = 0
        pending_count = 0
        
        for i, todo in enumerate(state["todos"], 1):
            status = "✓" if todo["completed"] else "○"
            if todo["completed"]:
                completed_count += 1
            else:
                pending_count += 1
            content_lines.append(f"{i}. [{status}] {todo['title']}")
            if todo.get("description"):
                content_lines.append(f"   Description: {todo['description']}")
            if todo.get("priority"):
                content_lines.append(f"   Priority: {todo['priority']}")
            if todo.get("due_date"):
                content_lines.append(f"   Due: {todo['due_date']}")
            content_lines.append("")
        
        content_lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        content = "\n".join(content_lines)
        state["files"][filename] = content
        
        return {
            "success": True, 
            "action": "exported_todos",
            "filename": filename,
            "total_tasks": len(state["todos"]),
            "completed": completed_count,
            "pending": pending_count,
            "summary": f"Exported {len(state['todos'])} tasks ({pending_count} pending, {completed_count} completed) to '{filename}'"
        }

# ═══════════════════════════════════════════════════════════════════════════════
# LLM REASONING ENGINE - FIXED WITH NARRATION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

# ✅ FIX 3: Updated system prompt with strict narration rules
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

def parse_relative_date(text: str, reference_date: datetime = None) -> str:
    """Parse relative dates like 'tomorrow', 'next monday'"""
    today = reference_date or datetime.now()
    text_lower = text.lower()
    
    if "tomorrow" in text_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text_lower:
        return today.strftime("%Y-%m-%d")
    elif "next week" in text_lower:
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    elif "next month" in text_lower:
        return (today + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Try to find day names
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if day in text_lower:
            current_day = today.weekday()
            days_ahead = i - current_day
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    return today.strftime("%Y-%m-%d")

def call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()


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

def format_message_history(messages: list) -> str:
    """Format message history for context"""
    history = []
    for msg in messages:
        if hasattr(msg, 'content'):
            role = "User" if msg.type == "human" else "Assistant"
            history.append(f"{role}: {msg.content[:200]}")  # Truncate long messages
    return "\n".join(history) if history else "No previous messages"

# ═══════════════════════════════════════════════════════════════════════════════
# LANGGRAPH AGENT WORKFLOW - FIXED
# ═══════════════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS - FIXED
# ═══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    messages: list
    todos: list
    files: dict
    calendar: list

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Get or create session
        state = get_or_create_session(request.session_id)
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=request.message))
        
        # Run the agent (assistant message is added INSIDE reasoning_node now)
        result = agent.invoke(state)
        
        # Update session with result
        sessions[request.session_id] = result
        
        # ✅ FIX 4: Format messages correctly for frontend
        formatted_messages = []
        for msg in result["messages"]:
            formatted_messages.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        
        # ✅ The last message IS the assistant response (added in reasoning_node)
        last_assistant_response = ""
        for msg in reversed(result["messages"]):
            if msg.type == "ai":
                last_assistant_response = msg.content
                break
        
        return ChatResponse(
            response=last_assistant_response,  # ✅ This is the rich narration
            messages=formatted_messages,
            todos=result["todos"],
            files=result["files"],
            calendar=result["calendar"]
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state"""
    state = get_or_create_session(session_id)
    return {
        "todos": state["todos"],
        "files": state["files"],
        "calendar": state["calendar"],
        "context": state["context"]
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "autonomous-ai-agent-v3", "version": "3.0.0"}

# ═══════════════════════════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
