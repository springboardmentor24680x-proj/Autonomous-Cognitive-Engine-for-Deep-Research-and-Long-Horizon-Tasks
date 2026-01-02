



import os
from groq import Groq
from langsmith import traceable

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

@traceable(name="event_extraction")
def extract_event(text: str):
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return res.choices[0].message.content.strip()
