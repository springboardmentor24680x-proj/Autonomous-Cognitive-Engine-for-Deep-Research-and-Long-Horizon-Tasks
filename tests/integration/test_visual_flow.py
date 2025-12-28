def test_visual_generation_flow():
    agent = setup_agent()
    
    # Trigger the full chain
    agent.invoke([
        HumanMessage(content="Research coffee market shares in India and create a pie chart.")
    ])
    
    # Check if the PNG was created in the VFS
    files = ls()
    assert any(f.endswith("_pie.png") for f in files)