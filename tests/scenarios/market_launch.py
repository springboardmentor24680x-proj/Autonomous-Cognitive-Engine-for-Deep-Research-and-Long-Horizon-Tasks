from src.main.app import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import read_file, ls, clear_vfs

def test_market_launch_scenario():
    clear_vfs()
    agent = setup_agent()

    prompts = [
        "Research specialty coffee competitors and save findings",
        "Summarize the research",
        "Create a business todo list based on the strategy",
    ]

    for p in prompts:
        agent.invoke([HumanMessage(content=p)])

    files = ls()
    assert "research_notes.txt" in files
    assert any("todos" in f for f in files)
