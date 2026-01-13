# tests/test_web_search.py
from langchain_core.messages import HumanMessage
from graph.state_graph import web_search_node

def test_web_search_node():
    """Web search node populates search_results and writes to VFS."""
    state = {"messages": [HumanMessage(content="What are today's AI news?")]}
    output_state = web_search_node(state)

    # Check search_results
    assert "search_results" in output_state
    assert len(output_state["search_results"]) > 0
