





import os
from groq import Groq
from langsmith import traceable
from src.memory.vfs import read_file, append_file

# Initialize Groq client using API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt defining summarization behavior
PROMPT = """
Summarize the following research.
Rules:
- Bullet points
- Concise
"""

@traceable(
    name="summarization_subagent",
    run_type="tool"
)
def run_summary() -> str:
    """
    Summarizes stored research content and saves the result.
    """

    # Read previously stored research data
    content = read_file("research.md")

    # Handle case when no research exists
    if not content:
        return "No research content found to summarize."

    # Send summarization request to the LLM
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},  # Summarization rules
            {"role": "user", "content": content}    # Research content
        ],
        temperature=0  # Deterministic, concise output
    )

    # Extract summary output
    output = res.choices[0].message.content.strip()

    # Store summary in virtual file system
    append_file("summary.md", output)

    # Return summary
    return output
