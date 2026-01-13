# tests/test_routing.py
from graph.state_graph import ResearchAgent
from langchain_core.messages import HumanMessage

def test_basic_research_response(chatbot_state):
    # Use the fixture as the base state
    state = dict(chatbot_state)  # copy

    # Append your test message
    state["messages"].append(HumanMessage(content="Explain recursion"))

    # Invoke agent
    output_state = ResearchAgent.invoke(state)

    response = output_state["messages"][-1].content.lower()

    assert "recursion" in response
