from src.main.app import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import ls, clear_vfs

def test_long_horizon_execution():
    clear_vfs()
    agent = setup_agent()

    prompts = [
        "Research AI agents market",
        "Save risks and opportunities",
        "Summarize findings",
        "Create a 30-day learning todo plan",
        "Schedule a review meeting next Friday at 5 PM"
    ]

    for p in prompts:
        agent.invoke([HumanMessage(content=p)])

    files = ls()
    assert len(files) >= 2  # research + todos
