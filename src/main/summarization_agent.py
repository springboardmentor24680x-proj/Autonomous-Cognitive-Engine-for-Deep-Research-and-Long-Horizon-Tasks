




import os
from groq import Groq
from langsmith import traceable
from src.memory.vfs import read_file, append_file

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """
Summarize the following research.
Rules:
- Bullet points
- Concise
"""

@traceable(name="summarization_subagent")
def run_summary() -> str:
    content = read_file("research.md")

    if not content:
        return "No research content found to summarize."

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": content}
        ],
        temperature=0
    )

    output = res.choices[0].message.content.strip()
    append_file("summary.md", output)
    return output
