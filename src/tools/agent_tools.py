from dotenv import load_dotenv
load_dotenv()

from typing import List
from langsmith import traceable
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)


@traceable(name="Planner Tool", run_type="tool")
def planner_tool(messages: List[HumanMessage], active: bool) -> str:
    if not active:
        return "Skipped"
    return llm.invoke([
        SystemMessage(content="Create a clear step-by-step plan using full conversation context."),
        *messages
    ]).content


@traceable(name="Search Tool", run_type="tool")
def search_tool(messages: List[HumanMessage], active: bool) -> str:
    if not active:
        return "Skipped"
    return llm.invoke([
        SystemMessage(content="Give 3–5 relevant websites with short descriptions."),
        *messages
    ]).content


@traceable(name="Summarizer Tool", run_type="tool")
def summarizer_tool(messages: List[HumanMessage], active: bool) -> str:
    if not active:
        return "Skipped"
    return llm.invoke([
        SystemMessage(content="Summarize the conversation in simple bullet points."),
        *messages
    ]).content