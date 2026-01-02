


def route_task(text: str) -> str:
    t = text.lower()

    # IMPORTANT: summary FIRST
    if any(k in t for k in ["summarize", "summary", "tl;dr", "shorten"]):
        return "summary"

    if any(k in t for k in ["research", "analyze", "investigate", "find"]):
        return "research"

    if any(k in t for k in ["schedule", "meeting", "event", "remind"]):
        return "calendar"

    return "default"
