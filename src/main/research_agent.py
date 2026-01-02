

import os
from groq import Groq
from langsmith import traceable
from src.memory.vfs import append_file

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """
You are a research sub-agent.
Rules:
- Bullet points only
- Factual
- No hallucinations
"""

@traceable(name="research_subagent")
def run_research(query: str) -> str:
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": query}
        ],
        temperature=0.2
    )

    output = res.choices[0].message.content.strip()
    append_file("research.md", output)
    return output
