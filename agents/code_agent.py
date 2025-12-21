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

def write_code(task: str) -> str:
    messages = [
        SystemMessage(content="You are a coding expert."),
        HumanMessage(content=task)
    ]
    return llm.invoke(messages).content
