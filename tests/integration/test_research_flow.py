from src.main.app import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import read_file, clear_vfs

def setup_function():
    clear_vfs()

def test_research_and_persistence():
    agent = setup_agent()

    agent.invoke([
        HumanMessage(content="Research specialty coffee brands in India")
    ])

    content = read_file("research_notes.txt")
    assert "coffee" in content.lower()
