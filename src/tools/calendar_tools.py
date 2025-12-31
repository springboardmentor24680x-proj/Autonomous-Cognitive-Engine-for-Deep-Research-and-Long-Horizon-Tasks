EVENTS = []

def add_event(title: str, date: str, time: str):
    EVENTS.append({
        "title": title,
        "date": date,
        "time": time
    })
    return f"Event '{title}' scheduled on {date} at {time}"
