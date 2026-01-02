def test_web_search_agent(monkeypatch):
    def mock_search_web(query):
        return {
            "organic_results": [
                {
                    "title": "Mock Result",
                    "snippet": "This is a mocked snippet",
                    "link": "https://example.com"
                }
            ]
        }

    monkeypatch.setattr(
        "agents.web_search_agent.search_web",
        mock_search_web
    )

    from agents.web_search_agent import web_search_agent

    result = web_search_agent("LangGraph")

    assert "Mock Result" in result
    assert "mocked snippet" in result.lower()
