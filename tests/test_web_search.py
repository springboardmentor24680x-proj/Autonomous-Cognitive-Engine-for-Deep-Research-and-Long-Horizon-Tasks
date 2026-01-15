from langchain_core.messages import HumanMessage
from graph.web_search_graph import web_search_node
from graph.state import AgentState

def test_web_search_node(monkeypatch):

    # Mock TavilyClient.search
    def mock_search(self, query, **kwargs):
        return {
            "results": [
                {
                    "title": "AI News Today",
                    "url": "https://example.com",
                    "content": "AI is advancing rapidly in 2026."
                }
            ]
        }

    monkeypatch.setattr(
        "tavily.tavily.TavilyClient.search",
        mock_search
    )

    state = AgentState(input="What are today's AI news?")
    state["messages"] = [HumanMessage(content="What are today's AI news?")]

    output_state = web_search_node(state)

    # Assertions
    assert "search_results" in output_state
    assert output_state["search_results"] is not None
    assert len(output_state["search_results"]) > 0
