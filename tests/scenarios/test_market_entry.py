from langchain_core.messages import HumanMessage
from src.main.research_agent import setup_agent
from src.memory.vfs import read_file

def test_long_horizon_market_entry():
    agent = setup_agent()
    
    # 1. Research (Keep it simple to save tokens)
    agent.invoke([
        HumanMessage(content="Call research_task for 'Specialty coffee India' and save to research_notes.txt. Do not explain, just call the tool.")
    ])
    
    # 2. Force Summarization (The Critical Step)
    summary_response = agent.invoke([
        HumanMessage(content="Run summarize_file on 'research_notes.txt'. Tell me the exact filename it creates.")
    ])

    # 3. Create Todo
    agent.invoke([
        HumanMessage(content="Use 'create_work_todo' for the task 'Draft coffee business plan'.")
    ])

    # 4. Schedule
    agent.invoke([
        HumanMessage(content="Use 'add_event' for 'Business Plan Review' on 2024-05-20 at 10:00 AM.")
    ])

    # The tool names the file based on the input filename + _summary
    summary = read_file("research_notes_summary.txt") 
    todos = read_file("todos_work.txt")
    if "not found" in summary:
            print(f"\nAGENT FAILED. SAID: {summary_response['messages'][-1].content}")
    assert "not found" not in summary
    assert len(summary) > 50 # Now this will pass
    assert "Draft coffee business plan" in todos