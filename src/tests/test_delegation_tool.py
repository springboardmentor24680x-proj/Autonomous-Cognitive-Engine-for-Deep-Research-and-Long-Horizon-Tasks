import pytest
from agents.delegation_tool import delegate_task

def test_delegate_web_search(monkeypatch):
    def mock_web_agent(input_text):
        return f"Mocked web agent result for {input_text}"

    monkeypatch.setattr(
        "agents.delegation_tool.SUB_AGENT_REGISTRY",
        {"web_search": mock_web_agent}
    )

    result = delegate_task("web_search", "LangGraph")

    assert "Mocked web agent result" in result
