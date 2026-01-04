

def route_task(text: str) -> str:
    """
    Identifies the task type from user input using keywords.
    """

    # Convert text to lowercase for case-insensitive matching
    t = text.lower()

    # Check for summarization requests (highest priority)
    if any(k in t for k in ["summarize", "summary", "tl;dr", "shorten"]):
        return "summary"

    # Check for research or analysis requests
    if any(k in t for k in ["research", "analyze", "investigate", "find"]):
        return "research"

    # Check for scheduling or reminder-related requests
    if any(k in t for k in ["schedule", "meeting", "event", "remind"]):
        return "calendar"

    # Default task if no keywords match
    return "default"
