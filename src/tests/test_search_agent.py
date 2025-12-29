import pytest
from agents.search_agent import SearchAgent

def test_search_agent(monkeypatch):
    def mock_web_search(query):
        return f"Mocked search result for: {query}"

    monkeypatch.setattr(
        "agents.search_agent.web_search",
        mock_web_search
    )

    result = SearchAgent.invoke({"query": "LangGraph"})

    assert "result" in result
    assert "Mocked search result" in result["result"]
