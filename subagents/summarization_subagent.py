from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
SUMMARY_PROMPT = """
You are a summarization sub-agent.

Rules:
- Summarize the provided content clearly and concisely
- Do NOT add new information
- Do NOT perform research
- Preserve key facts and structure
"""

def build_summarization_agent(groq_client):
    # ChatPromptTemplate correctly maps dictionary inputs to placeholders
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUMMARY_PROMPT),
        ("human", "{input}") 
    ])

    # Adding StrOutputParser ensures the tool receives a string, not a Message object
    return prompt | groq_client | StrOutputParser()
