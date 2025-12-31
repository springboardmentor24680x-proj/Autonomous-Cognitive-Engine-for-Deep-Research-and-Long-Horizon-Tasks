from groq import Groq
import os
from langsmith import traceable

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FACT_PROMPT = """
Extract only IMPORTANT long-term facts about the user.
Ignore casual chat.

Rules:
- Bullet points only
- No assumptions
- If nothing important, output NONE
"""

@traceable(name="fact_extraction")
def extract_facts(text: str) -> str:
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": FACT_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )

    return res.choices[0].message.content.strip()
