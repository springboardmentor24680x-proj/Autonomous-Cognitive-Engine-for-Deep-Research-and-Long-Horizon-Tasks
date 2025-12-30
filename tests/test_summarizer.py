from core_app import invoke_chat

def test_web_search_then_summarize(chatbot_state):
    state = invoke_chat(
        chatbot_state,
        "Search the web and summarize today's AI news"
    )

    summary = state["messages"][-1].content
    assert len(summary.split("\n")) <= 10


def test_direct_summarization(chatbot_state):
    text = (
        "LangGraph allows building multi-agent workflows. "
        "It supports conditional routing and state management."
    )

    state = invoke_chat(
        chatbot_state,
        f"Summarize in 2 lines:\n{text}"
    )

    summary = state["messages"][-1].content
    assert len(summary.split("\n")) <= 2
