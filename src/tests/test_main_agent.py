from agent import run_agent, initial_state
from langchain_core.messages import HumanMessage


def test_main_agent_basic():
    state = initial_state()
    state["messages"].append(
        HumanMessage(content="hi")
    )

    result = run_agent(state)

    assert "help" in result["final_answer"].lower()