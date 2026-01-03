from agent import run_agent, initial_state
from langchain_core.messages import HumanMessage


def test_search_agent_delegation():
    state = initial_state()
    state["messages"].append(
        HumanMessage(content="Provide web links for LangSmith")
    )

    result = run_agent(state)

    assert "http" in result["final_answer"].lower()