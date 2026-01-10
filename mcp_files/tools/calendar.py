# tools/calendar.py
_EVENTS = []

def add_event(title: str, date: str, time: str) -> str:
    _EVENTS.append({
        "title": title,
        "date": date,
        "time": time
    })
    return "Event added"

def list_events() -> list:
    return _EVENTS
