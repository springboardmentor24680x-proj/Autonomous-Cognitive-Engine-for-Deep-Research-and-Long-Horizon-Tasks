from groq import Groq
import os
from langsmith import traceable

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EVENT_PROMPT = """
Extract calendar events if present.

Return STRICT JSON:
{
  "title": "...",
  "date": "...",
  "time": "..."
}

If no event exists, return NONE.
"""

@traceable(name="event_extraction")
def extract_event(text: str):
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": EVENT_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )

    content = res.choices[0].message.content.strip()
    return content
