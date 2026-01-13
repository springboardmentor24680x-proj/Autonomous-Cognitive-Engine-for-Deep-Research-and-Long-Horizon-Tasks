# tests/test_summarizer.py
from langchain_core.messages import HumanMessage
from graph.state_graph import summarizer_node

def test_summarizer_node():
    """Summarizer works on pre-filled search_results."""
    state = {
        "messages": [HumanMessage(content="Please summarize this content")],
        "search_results": "LangGraph allows building multi-agent workflows. It supports conditional routing and state management."
    }

    output_state = summarizer_node(state)
    last_msg = output_state["messages"][-1]

    from langchain_core.messages import AIMessage
    assert isinstance(last_msg, AIMessage)
    assert len(last_msg.content) > 0
