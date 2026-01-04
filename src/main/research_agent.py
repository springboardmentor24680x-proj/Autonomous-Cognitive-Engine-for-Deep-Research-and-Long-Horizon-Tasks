
import os
from groq import Groq
from langsmith import traceable
from src.memory.vfs import append_file

# Initialize Groq client using API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt defining research agent behavior
PROMPT = """
You are a research sub-agent.
Rules:
- Bullet points only
- Factual
- No hallucinations
"""

@traceable(name="research_subagent", run_type="tool")
def run_research(query: str) -> str:
    """
    Performs factual research and stores results in memory.
    """

    # Send research query to the LLM
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},  # Research rules
            {"role": "user", "content": query}      # Research query
        ],
        temperature=0.2  # Low randomness for factual accuracy
    )

    # Extract model output
    output = res.choices[0].message.content.strip()

    # Persist research findings to virtual file system
    append_file("research.md", output)

    # Return research results
    return output
