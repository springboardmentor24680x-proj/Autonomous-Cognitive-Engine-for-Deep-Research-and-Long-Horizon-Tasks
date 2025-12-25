from unittest.mock import MagicMock, patch
from agents.supervisor_agent import SupervisorAgent


def test_supervisor_agent_integration():
    """
    Integration Test:
    planner -> search -> respond -> summarize
    """

    # Fake LLM response
    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = "This is the final AI answer."

    with patch("agents.supervisor_agent.llm", fake_llm), \
         patch("agents.supervisor_agent.SearchAgent.invoke") as mock_search, \
         patch("agents.supervisor_agent.SummarizerAgent.invoke") as mock_summarizer, \
         patch("agents.supervisor_agent.load_memory", return_value=[]), \
         patch("agents.supervisor_agent.append_memory"):


        # Mock search agent output
        mock_search.return_value = {
            "result": "MCP is a protocol used for connecting AI models to tools."
        }

        # Mock summarizer output
        mock_summarizer.return_value = {
            "output": "MCP connects AI models to tools safely."
        }

        # Run the full graph
        result = SupervisorAgent.invoke({
            "input": "Explain MCP"
        })

    # Assertions
    assert "output" in result
    assert "This is the final AI answer." in result["output"]
    assert "Summary" in result["output"]
    assert "MCP connects AI models" in result["output"]
