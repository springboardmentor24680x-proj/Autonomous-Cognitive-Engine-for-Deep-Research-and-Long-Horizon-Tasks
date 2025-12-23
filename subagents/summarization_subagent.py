from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

SUMMARY_PROMPT = """
You are a summarization sub-agent.

Rules:
- Summarize the provided content clearly and concisely
- Do NOT add new information
- Do NOT perform research
- Preserve key facts and structure
"""

def build_summarization_agent(groq_client):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUMMARY_PROMPT),
        ("human", "{input}") 
    ])

    # Ensure the model is bound to the chain correctly
    return prompt | groq_client
