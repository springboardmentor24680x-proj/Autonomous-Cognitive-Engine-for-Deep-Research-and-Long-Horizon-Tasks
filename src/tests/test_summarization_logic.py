from agent import run_agent, initial_state
from langchain_core.messages import HumanMessage


def test_summarizer_agent():
    state = initial_state()
    state["messages"].append(
        HumanMessage(content="Summarize LangSmith tracing")
    )

    result = run_agent(state)

    assert len(result["final_answer"]) > 20