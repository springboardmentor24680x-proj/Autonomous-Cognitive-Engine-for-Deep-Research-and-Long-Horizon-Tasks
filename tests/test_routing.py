from langchain_core.messages import HumanMessage, AIMessage
from graph.state_graph import build_state_graph
from graph.state import AgentState

def test_basic_research_response():
    graph = build_state_graph()

    state = AgentState(input="Explain recursion")
    state["messages"] = [HumanMessage(content="Explain recursion")]

    final_state = graph.invoke(state)

    # Ensure messages exist
    assert "messages" in final_state
    assert len(final_state["messages"]) >= 2

    # Last message must be AI response
    last_message = final_state["messages"][-1]
    assert isinstance(last_message, AIMessage)

    # Validate content
    assert last_message.content is not None
    assert isinstance(last_message.content, str)
    assert len(last_message.content) > 0
