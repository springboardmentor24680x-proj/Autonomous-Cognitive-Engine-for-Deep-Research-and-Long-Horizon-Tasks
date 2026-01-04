

import os
from groq import Groq
from langsmith import traceable

# Initialize Groq client with API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt instructing the model to extract calendar event details
PROMPT = """
Extract calendar events.
Return STRICT JSON:
{
  "title": "...",
  "date": "...",
  "time": "..."
}
If none, return NONE.
"""

@traceable(
    name="event_extraction",
    run_type="tool"
)
def extract_event(text: str):
    """
    Extracts calendar event information from user text.
    """

    # Send extraction request to the LLM
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},  # Extraction rules
            {"role": "user", "content": text}       # User input
        ],
        temperature=0  # Deterministic output for structured JSON
    )

    # Return extracted event data or NONE
    return res.choices[0].message.content.strip()
