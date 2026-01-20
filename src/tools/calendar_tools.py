import streamlit as st


# ----------------------------
# In-memory calendar
# ----------------------------
if "EVENTS" not in st.session_state:
    st.session_state["EVENTS"] = []

EVENTS = st.session_state["EVENTS"]

def add_event(title: str, date: str, time: str) -> str:
    """Adds a new calendar event. Inputs: title (str), date (YYYY-MM-DD), time (str)."""
    for event in EVENTS:
        if event["title"] == title and event["date"] == date and event["time"] == time:
            return "Event already exists. Skipping duplicate."
        
    EVENTS.append({
        "title": title,
        "date": date,
        "time": time
    })
    return f"Event '{title}' added on {date} at {time}."


def list_events() -> str:
    """Retrieves and lists all scheduled events from the calendar."""
    if not EVENTS:
        return "No events scheduled."

    result = []
    for i, e in enumerate(EVENTS):
        result.append(f"{i}: {e['title']} on {e['date']} at {e['time']}")
    return "\n".join(result)


def delete_event(index: int) -> str:
    """Deletes a calendar event by its index number. Input: index (int)."""
    try:
        event = EVENTS.pop(index)
        return f"Deleted event '{event['title']}'."
    except IndexError:
        return "Invalid event index."
