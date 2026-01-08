#mcp_calendar_tools.py
from pydantic import BaseModel
from typing import List, Optional
from my_mcp.server.fastapi import MCPServer

# ----------------------------
# Calendar Storage (In-Memory)
# ----------------------------
class CalendarStore:
    def __init__(self):
        self.events = []

CALENDAR = CalendarStore()

# ----------------------------
# Input Schemas
# ----------------------------
class AddEventInput(BaseModel):
    title: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM

class DeleteEventInput(BaseModel):
    index: int

class ListEventsInput(BaseModel):
    # Empty model to ensure consistent JSON-body handling
    pass

# ----------------------------
# MCP Tool Registration
# ----------------------------
def register_calendar_tools(server: MCPServer):

    @server.tool()
    def add_event(input: AddEventInput) -> str:
        # Check for exact duplicates
        for event in CALENDAR.events:
            if (
                event["title"] == input.title
                and event["date"] == input.date
                and event["time"] == input.time
            ):
                return "Event already exists. Skipping duplicate."

        CALENDAR.events.append({
            "title": input.title,
            "date": input.date,
            "time": input.time
        })
        return f"Event '{input.title}' added on {input.date} at {input.time}."

    @server.tool()
    def list_events(input: Optional[ListEventsInput] = None) -> str:
        if not CALENDAR.events:
            return "No events scheduled."

        return "\n".join(
            f"{i}: {e['title']} on {e['date']} at {e['time']}"
            for i, e in enumerate(CALENDAR.events)
        )

    @server.tool()
    def delete_event(input: DeleteEventInput) -> str:
        try:
            event = CALENDAR.events.pop(input.index)
            return f"Deleted event '{event['title']}'."
        except IndexError:
            return f"Invalid index {input.index}. Use list_events to see valid IDs."