
import os
from groq import Groq
from langsmith import traceable

# Initialize Groq client using API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt instructing the model to extract long-term important user facts
PROMPT = """
Extract IMPORTANT long-term user facts.
Rules:
- Bullet points only
- If none, return NONE
"""

@traceable(
    name="fact_extraction",
    run_type="tool"
)
def extract_facts(text: str) -> str:
    """
    Extracts important long-term user facts from input text.
    """

    # Send fact extraction request to the LLM
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT},  # Extraction rules
            {"role": "user", "content": text}       # User input
        ],
        temperature=0  # Deterministic output for consistent facts
    )

    # Return extracted facts or NONE
    return res.choices[0].message.content.strip()





