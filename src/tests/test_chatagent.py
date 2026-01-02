import pytest
from agents.chat_agent import handle_message

def test_chat_agent_delegation(monkeypatch):
    def mock_delegate(task_type, text):
        return f"Mocked delegate result for {task_type}"

    # Replace delegate_task used inside chat_agent
    monkeypatch.setattr(
        "agents.chat_agent.delegate_task",
        mock_delegate
    )

    state = {}
    state, reply = handle_message(state, "search ai tools")

    assert "Delegated" in reply
