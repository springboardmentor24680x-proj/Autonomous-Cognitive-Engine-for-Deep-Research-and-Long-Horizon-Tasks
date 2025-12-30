from core_app import invoke_chat

def test_basic_llm_response(chatbot_state):
    state = invoke_chat(chatbot_state, "Explain recursion")

    response = state["messages"][-1].content.lower()
    assert "recursion" in response
