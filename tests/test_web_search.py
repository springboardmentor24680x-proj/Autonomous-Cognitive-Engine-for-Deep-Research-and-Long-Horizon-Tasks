from core_app import invoke_chat

def test_web_search_is_used(chatbot_state):
    state = invoke_chat(
        chatbot_state,
        "What are today's AI news?"
    )

    response = state["messages"][-1].content.lower()
    assert response is not None
