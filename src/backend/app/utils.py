import os
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict, Any
import re

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# =========================================================
# GROQ CONFIG
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not set")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    timeout=30.0  # Add timeout to prevent hanging
)


def call_gemini(prompt: str, temperature: float = 0.3, max_tokens: int = 1024) -> str:
    """
    Call Groq API with timeout protection
    
    Args:
        prompt: The prompt to send
        temperature: Creativity level (0-1)
        max_tokens: Maximum response length (reduced default for speed)
    
    Returns:
        Generated text response
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful, precise, and concise AI assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30  # Explicit timeout
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  Error calling Groq API: {e}")
        return f"I encountered an error: {str(e)}"


# =========================================================
# AGENT STATE
# =========================================================

class AgentState(TypedDict):
    messages: List[Any]
    todos: List[Dict[str, Any]]
    calendar: List[Dict[str, Any]]
    files: Dict[str, str]
    visualizations: List[Dict[str, Any]]
    context: Dict[str, Any]


# =========================================================
# SESSION MANAGEMENT
# =========================================================

sessions: Dict[str, AgentState] = {}


def get_or_create_session(session_id: str) -> AgentState:
    """Get existing session or create new one"""
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "todos": [],
            "calendar": [],
            "files": {},
            "visualizations": [],
            "context": {}
        }
    return sessions[session_id]


def clear_session(session_id: str) -> bool:
    """Clear a specific session"""
    if session_id in sessions:
        del sessions[session_id]
        return True
    return False


def list_sessions() -> List[str]:
    """List all active session IDs"""
    return list(sessions.keys())


# =========================================================
# DATE PARSING
# =========================================================

def parse_relative_date(text: str) -> str:
    """
    Parse relative date strings into YYYY-MM-DD format
    
    Supports:
    - "today" -> current date
    - "tomorrow" -> next day
    - "in X days" -> X days from now
    - "next week" -> 7 days from now
    - "next month" -> 30 days from now
    - Actual dates pass through unchanged
    """
    if not text:
        return ""

    today = datetime.now()
    text = text.lower().strip()

    # Handle "today"
    if "today" in text:
        return today.strftime("%Y-%m-%d")
    
    # Handle "tomorrow"
    if "tomorrow" in text:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Handle "yesterday"
    if "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Handle "in X days"
    match = re.search(r"in (\d+) days?", text)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Handle "next week"
    if "next week" in text:
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Handle "next month"
    if "next month" in text:
        return (today + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Handle "this friday", "next monday", etc.
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in text:
            current_day = today.weekday()
            days_ahead = day_num - current_day
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    # If already in YYYY-MM-DD format or another format, return as is
    return text


def parse_time(text: str) -> str:
    """
    Parse time strings into HH:MM format
    
    Supports:
    - "3pm" -> "15:00"
    - "3:30pm" -> "15:30"
    - "15:00" -> "15:00"
    - "noon" -> "12:00"
    - "midnight" -> "00:00"
    """
    if not text:
        return "09:00"
    
    text = text.lower().strip()
    
    # Handle special cases
    if "noon" in text:
        return "12:00"
    if "midnight" in text:
        return "00:00"
    
    # Handle 12-hour format with am/pm
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", text)
    if match:
        hour = int(match.group(1))
        minute = match.group(2) or "00"
        period = match.group(3)
        
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        
        return f"{hour:02d}:{minute}"
    
    # Handle 24-hour format
    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return f"{hour:02d}:{minute:02d}"
    
    # Default fallback
    return "09:00"


# =========================================================
# MESSAGE FORMATTER
# =========================================================

def format_message_history(messages: List[Any], max_length: int = 10) -> str:
    """
    Format message history for display or context
    
    Args:
        messages: List of messages
        max_length: Maximum number of messages to include
    
    Returns:
        Formatted string of conversation history
    """
    if not messages:
        return "No prior conversation."
    
    # Take only recent messages
    recent_messages = messages[-max_length:] if len(messages) > max_length else messages
    
    lines = []
    for msg in recent_messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            # Truncate long responses
            content = msg.content
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"Assistant: {content}")
        elif isinstance(msg, dict):
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


# =========================================================
# STATE HELPERS
# =========================================================

def get_pending_todos(state: AgentState) -> List[Dict[str, Any]]:
    """Get all pending (not completed) todos"""
    return [t for t in state["todos"] if not t.get("completed", False)]


def get_completed_todos(state: AgentState) -> List[Dict[str, Any]]:
    """Get all completed todos"""
    return [t for t in state["todos"] if t.get("completed", False)]


def get_high_priority_todos(state: AgentState) -> List[Dict[str, Any]]:
    """Get all high priority todos"""
    return [t for t in state["todos"] if t.get("priority") == "high" and not t.get("completed")]


def get_upcoming_events(state: AgentState, days: int = 7) -> List[Dict[str, Any]]:
    """Get calendar events in the next X days"""
    today = datetime.now()
    upcoming = []
    
    for event in state["calendar"]:
        try:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            days_until = (event_date - today).days
            if 0 <= days_until <= days:
                upcoming.append(event)
        except:
            continue
    
    return sorted(upcoming, key=lambda e: e["date"])


def get_state_summary(state: AgentState) -> str:
    """Get a human-readable summary of current state"""
    pending = len(get_pending_todos(state))
    completed = len(get_completed_todos(state))
    high_priority = len(get_high_priority_todos(state))
    upcoming = len(get_upcoming_events(state))
    
    return f""" Current State:
- Tasks: {pending} pending, {completed} completed ({high_priority} high priority)
- Calendar: {len(state['calendar'])} events ({upcoming} upcoming)
- Files: {len(state['files'])} saved"""


# =========================================================
# VALIDATION HELPERS
# =========================================================

def validate_date(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False


def validate_time(time_str: str) -> bool:
    """Validate time string is in HH:MM format"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[/\\:*?"<>|]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure not empty
    if not filename:
        filename = "untitled"
    return filename