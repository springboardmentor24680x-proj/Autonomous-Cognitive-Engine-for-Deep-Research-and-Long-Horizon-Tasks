import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from graph.state import AgentState

@pytest.fixture
def chatbot_state():
    return AgentState(input="")
