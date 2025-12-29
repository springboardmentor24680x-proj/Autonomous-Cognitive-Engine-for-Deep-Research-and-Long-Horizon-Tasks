import pytest
from agents.supervisor_agent import SupervisorAgent

def test_supervisor_agent(monkeypatch):
    # -------------------------
    # Mock SearchAgent
    # -------------------------
    def mock_search_invoke(state):
        return {"result": "Mocked search info"}

    monkeypatch.setattr(
        "agents.supervisor_agent.SearchAgent.invoke",
        mock_search_invoke
    )

    # -------------------------
    # Mock SummarizerAgent
    # -------------------------
    def mock_summarizer_invoke(state):
        return {"output": "Mocked summary"}

    monkeypatch.setattr(
        "agents.supervisor_agent.SummarizerAgent.invoke",
        mock_summarizer_invoke
    )

    # -------------------------
    # Mock memory
    # -------------------------
    monkeypatch.setattr(
        "memory.vfs.load_memory",
        lambda: []
    )

    monkeypatch.setattr(
        "memory.vfs.append_memory",
        lambda role, content: None
    )

    # -------------------------
    # Run agent
    # -------------------------
    result = SupervisorAgent.invoke({
        "input": "What is LangGraph?"
    })

    # -------------------------
    # Assertions
    # -------------------------
    assert "output" in result
    assert "Mocked summary" in result["output"]
