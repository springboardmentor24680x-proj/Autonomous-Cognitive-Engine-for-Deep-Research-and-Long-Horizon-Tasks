from src.main.app import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import read_file, clear_vfs

def setup_function():
    clear_vfs()

from src.memory.vfs import ls, read_file

def test_research_and_persistence():
    agent = setup_agent()

    agent.invoke([
        HumanMessage(content="Research specialty coffee brands in India")
    ])

    agent.invoke([
        HumanMessage(content="Proceed with the research")
    ])

    files = ls()
    research_files = [f for f in files if "coffee" in f or "research" in f]

    assert research_files, "No research file created"

    content = read_file(research_files[0])
    assert "coffee" in content.lower()
