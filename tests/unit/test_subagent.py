from subagents.research_subagent import build_research_agent
from subagents.summarization_subagent import build_summarization_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

def test_research_subagent_runs():
    model = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )
    agent = build_research_agent(model)

    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is specialty coffee?"}]
    })

    assert "coffee" in result["messages"][-1].content.lower()

def test_summarization_subagent_runs():
    model = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )
    agent = build_summarization_agent(model)

    result = agent.invoke({
        "input": "Coffee is brewed from roasted beans."
    })

    assert len(result) > 0