from graph.summarizer_graph import summary_node
from graph.state import AgentState

def test_summary_node():
    # Create AgentState with search results
    state = AgentState(
        input="Summarize this content",
        search_results="LangGraph allows building multi-agent workflows."
    )

    # Run summarizer
    output_state = summary_node(state)

    # Ensure summary exists in dict-based state
    assert "summary" in output_state

    # Validate summary content
    assert output_state["summary"] is not None
    assert isinstance(output_state["summary"], str)
    assert len(output_state["summary"]) > 0
