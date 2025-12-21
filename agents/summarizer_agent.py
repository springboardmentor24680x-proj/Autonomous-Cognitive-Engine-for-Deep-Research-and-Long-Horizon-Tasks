import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="gpt-4o-mini",
)

def summarize(text: str) -> str:
    messages = [
        SystemMessage(content="You summarize text concisely."),
        HumanMessage(content=text)
    ]
    return llm.invoke(messages).content
