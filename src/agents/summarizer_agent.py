from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

def summarizer_agent(text: str) -> str:
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        system_msg = SystemMessage(content="You are a Summarization Expert. Create a professional report.")
        response = llm.invoke([system_msg, HumanMessage(content=text)])
        return response.content
    except Exception as e:
        return f"Summarization Sub-Agent Error: {str(e)}"