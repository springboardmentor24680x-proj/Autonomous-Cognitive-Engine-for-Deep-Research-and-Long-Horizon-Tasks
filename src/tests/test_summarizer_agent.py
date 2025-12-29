from agents.summarizer_agent import SummarizerAgent

def test_summarizer_agent():
    state = {
        "input": "LangGraph is a framework for building stateful agents."
    }

    result = SummarizerAgent.invoke(state)

    assert "output" in result
    assert isinstance(result["output"], str)
    assert len(result["output"]) > 0
