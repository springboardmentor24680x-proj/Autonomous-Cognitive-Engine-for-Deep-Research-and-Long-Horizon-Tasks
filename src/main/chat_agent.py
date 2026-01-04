

import os
from groq import Groq
from langsmith import traceable

# Initialize Groq client using API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System-level instructions that guide the AI's behavior
SYSTEM_PROMPT = """
You are a helpful autonomous AI assistant.
Answer naturally like a chat assistant.
"""

@traceable(name="chat_subagent")
def run_chat(text: str) -> str:
    """
    Sends user input to the LLM and returns the chat response.
    """

    # Create a chat completion request
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},  # AI behavior rules
            {"role": "user", "content": text}              # User input
        ],
        temperature=0.4  # Controls randomness (lower = more deterministic)
    )

    # Return the model's reply as clean text
    return res.choices[0].message.content.strip()
