import sys
import os
import pytest

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from core_app import create_initial_state

@pytest.fixture
def chatbot_state():
    return create_initial_state()

