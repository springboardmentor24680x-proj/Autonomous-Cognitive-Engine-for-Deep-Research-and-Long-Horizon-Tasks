# src/tools/calendar_tools.py

from pydantic import BaseModel
from typing import List
from my_mcp.server.fastapi import MCPServer

# ----------------------------
# Calendar Storage (Scoped)
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


# ----------------------------
# MCP Tool Registration
# ----------------------------
def register_calendar_tools(server: MCPServer):

    @server.tool()
    def add_event(input: AddEventInput) -> str:
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
    def list_events() -> str:
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
            return "Invalid event index."
