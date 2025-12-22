from langchain_core.messages import SystemMessage, HumanMessage

SUMMARY_PROMPT = """
You are a summarization sub-agent.

Rules:
- Summarize the provided content clearly and concisely
- Do NOT add new information
- Do NOT perform research
- Preserve key facts and structure
"""

def build_summarization_agent(groq_client):
    return groq_client.bind(
        messages=[
            SystemMessage(content=SUMMARY_PROMPT)
        ]
    )
