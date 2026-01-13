# tests/conftest.py
import sys
import os
import pytest

# Add src folder to Python path so all modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Optional: define reusable pytest fixtures here if needed
# For example, a minimal chatbot state fixture
from graph.state import AgentState

@pytest.fixture
def chatbot_state():
    return {"messages": []}  # minimal initial state
