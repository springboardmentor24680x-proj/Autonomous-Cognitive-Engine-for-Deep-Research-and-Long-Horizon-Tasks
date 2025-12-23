import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Annotated, TypedDict, Literal
from pydantic import BaseModel
from google import genai
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
class AgentState(TypedDict):
    """The complete state of the agent - persisted across turns"""
    messages: Annotated[list, add_messages] # Conversation history (LangGraph managed)
    todos: list[dict] # Task list
    files: dict[str, str] # Saved files
    calendar: list[dict] # Calendar events
    context: dict # Contextual memory

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
                "last_tool_results": [], # ✅ FIX 2: Store tool results
                "user_preferences": {}
            }
        }
    return sessions[session_id]

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

def format_message_history(messages: list) -> str:
    """Format message history for context"""
    history = []
    for msg in messages:
        if hasattr(msg, 'content'):
            role = "User" if msg.type == "human" else "Assistant"
            history.append(f"{role}: {msg.content[:200]}") # Truncate long messages
    return "\n".join(history) if history else "No previous messages"