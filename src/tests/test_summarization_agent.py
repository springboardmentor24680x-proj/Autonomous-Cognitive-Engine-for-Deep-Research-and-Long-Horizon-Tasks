import pytest
from agents.summarization_agent import summarization_agent

def test_summarization_agent(monkeypatch):
    def mock_llm(prompt):
        return "Mocked summary output"

    monkeypatch.setattr(
        "agents.summarization_agent.call_llm",
        mock_llm
    )

    result = summarization_agent("Explain LangSmith")

    assert "Mocked summary" in result
