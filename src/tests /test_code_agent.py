import pytest
from agents.code_agent import code_agent

def test_code_agent(monkeypatch):
    def mock_llm(prompt):
        return "def binary_search(): pass"

    monkeypatch.setattr(
        "agents.code_agent.call_llm",
        mock_llm
    )

    result = code_agent("write binary search in python")

    assert "binary_search" in result

