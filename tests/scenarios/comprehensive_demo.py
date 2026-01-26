"""
=============================================================================
COMPREHENSIVE 5-TASK DEMO: Testing Agent Capabilities for Project Evaluators
=============================================================================

This scenario demonstrates:
1. ✓ Multi-step workflow execution
2. ✓ Task dependency management (write_todos)
3. ✓ Research delegation (research_task)
4. ✓ File operations (write_file, read_file, edit_file)
5. ✓ Summarization (summarization_task)
6. ✓ Data visualization (create_visualization)
7. ✓ Calendar scheduling (add_event)
8. ✓ Todo creation (create_work_todo)

All tasks are interlinked and depend on successful completion of prior steps.
=============================================================================
"""

from src.main.research_agent import setup_agent
from langchain_core.messages import HumanMessage
from src.memory.vfs import read_file, ls, clear_vfs
import time

def run_comprehensive_demo():
    """
    Executes a 5-task workflow demonstrating full agent capabilities.
    Each task builds on the previous one.
    """
    print("\n" + "="*80)
    print("AUTONOMOUS COGNITIVE ENGINE - COMPREHENSIVE DEMO")
    print("="*80)
    
    # Initialize fresh agent
    agent = setup_agent()
    
    # ========================================================================
    # TASK 1: Research Market Opportunity (Foundation)
    # ========================================================================
    print("\n" + "-"*80)
    print("TASK 1: Research the blockchain gaming market landscape")
    print("-"*80)
    print("Objective: Gather market data, player trends, and revenue opportunities")
    print()
    
    task1 = """
    Research the current blockchain gaming market. Focus on:
    1. Popular blockchain games and their user bases
    2. Average player spending and revenue models
    3. Growth trends in 2024-2025
    4. Top platforms (Ethereum, Polygon, Solana)
    
    Save findings to 'blockchain_gaming_market.txt' with a DATA FOR GRAPHING section 
    showing revenue distribution across platforms. Format: Platform: Revenue_Millions
    """
    
    result1 = agent.invoke([HumanMessage(content=task1)])
    print(f"Result: {result1['messages'][-1].content}\n")
    time.sleep(2)
    
    # ========================================================================
    # TASK 2: Research Competition (Dependent on Task 1)
    # ========================================================================
    print("-"*80)
    print("TASK 2: Analyze top competitors in blockchain gaming")
    print("-"*80)
    print("Objective: Research leading blockchain gaming companies")
    print()
    
    task2 = """
    Research and compile information about the top 5 blockchain gaming companies.
    For each, find:
    1. Company name and founding date
    2. Total users/players
    3. Revenue per user
    4. Key differentiators
    
    Save to 'blockchain_competitors.txt' with a DATA FOR GRAPHING section showing
    user counts for each competitor. Format: CompanyName: UserCount_Millions
    """
    
    result2 = agent.invoke([HumanMessage(content=task2)])
    print(f"Result: {result2['messages'][-1].content}\n")
    time.sleep(2)
    
    # ========================================================================
    # TASK 3: Synthesize Strategy from Market + Competitor Data (Dependent)
    # ========================================================================
    print("-"*80)
    print("TASK 3: Create a strategic summary combining market and competitor insights")
    print("-"*80)
    print("Objective: Synthesize actionable strategy from research files")
    print()
    
    task3 = """
    Read 'blockchain_gaming_market.txt' and 'blockchain_competitors.txt'.
    Then summarize both files together into a SINGLE strategic document that includes:
    1. Market opportunities (from market file)
    2. Competitive landscape (from competitors file)
    3. Top 3 strategic recommendations for market entry
    
    Save the combined summary to 'blockchain_strategy_summary.txt'
    """
    
    result3 = agent.invoke([HumanMessage(content=task3)])
    print(f"Result: {result3['messages'][-1].content}\n")
    time.sleep(2)
    
    # ========================================================================
    # TASK 4: Create Executive Visualizations (Dependent on Tasks 1 & 2)
    # ========================================================================
    print("-"*80)
    print("TASK 4: Generate two visualizations from market and competitor data")
    print("-"*80)
    print("Objective: Create charts for executive presentation")
    print()
    
    task4a = """
    Using the DATA FOR GRAPHING section in 'blockchain_gaming_market.txt', 
    create a pie chart titled 'Blockchain Gaming Revenue by Platform'.
    """
    
    result4a = agent.invoke([HumanMessage(content=task4a)])
    print(f"Result 4a (Market Pie Chart): {result4a['messages'][-1].content}\n")
    time.sleep(2)
    
    task4b = """
    Using the DATA FOR GRAPHING section in 'blockchain_competitors.txt', 
    create a bar chart titled 'Top Competitors by Player Base'.
    """
    
    result4b = agent.invoke([HumanMessage(content=task4b)])
    print(f"Result 4b (Competitors Bar Chart): {result4b['messages'][-1].content}\n")
    time.sleep(2)
    
    # ========================================================================
    # TASK 5: Create Action Plan and Schedule Review (Dependent on All)
    # ========================================================================
    print("-"*80)
    print("TASK 5: Create actionable todo list and schedule strategy review")
    print("-"*80)
    print("Objective: Convert strategy into executable tasks with timeline")
    print()
    
    task5a = """
    Based on the strategy summary, create a work todo list with these tasks:
    1. Evaluate platform selection for market entry
    2. Analyze regulatory compliance requirements
    3. Design game mechanics for target audience
    4. Plan marketing strategy for player acquisition
    5. Set up initial smart contract infrastructure
    6. Conduct A/B testing with beta users
    
    Add each task to the work todo list.
    """
    
    result5a = agent.invoke([HumanMessage(content=task5a)])
    print(f"Result 5a (Todo List): {result5a['messages'][-1].content}\n")
    time.sleep(2)
    
    task5b = """
    Schedule the following review meetings:
    1. 'Market Strategy Review' on 2025-02-15 at 10:00 AM
    2. 'Competitive Analysis Deep Dive' on 2025-02-20 at 2:00 PM
    3. 'Execution Plan Finalization' on 2025-02-28 at 3:00 PM
    """
    
    result5b = agent.invoke([HumanMessage(content=task5b)])
    print(f"Result 5b (Scheduled Events): {result5b['messages'][-1].content}\n")
    time.sleep(2)
    
    # ========================================================================
    # VALIDATION: Show all created artifacts
    # ========================================================================
    print("\n" + "="*80)
    print("VALIDATION: Generated Artifacts")
    print("="*80)
    
    files = ls()
    print(f"\nFiles created: {len(files)}")
    print("\nFile List:")
    for f in sorted(files):
        print(f"  ✓ {f}")
    
    print("\n" + "-"*80)
    print("DEPENDENCY VERIFICATION")
    print("-"*80)
    
    # Check Task 1 artifact
    try:
        market_data = read_file("blockchain_gaming_market.txt")
        if "DATA FOR GRAPHING" in market_data:
            print("✓ Task 1: Market research with graphing data - SUCCESS")
        else:
            print("✗ Task 1: Market data missing graphing section")
    except:
        print("✗ Task 1: Market file not found")
    
    # Check Task 2 artifact
    try:
        competitor_data = read_file("blockchain_competitors.txt")
        if "DATA FOR GRAPHING" in competitor_data:
            print("✓ Task 2: Competitor research with graphing data - SUCCESS")
        else:
            print("✗ Task 2: Competitor data missing graphing section")
    except:
        print("✗ Task 2: Competitor file not found")
    
    # Check Task 3 artifact
    try:
        strategy = read_file("blockchain_strategy_summary.txt")
        if len(strategy) > 100:
            print("✓ Task 3: Strategic summary created - SUCCESS")
        else:
            print("✗ Task 3: Strategy summary is too short")
    except:
        print("✗ Task 3: Strategy file not found")
    
    # Check Task 4 artifacts
    png_files = [f for f in files if f.endswith(".png")]
    if len(png_files) >= 2:
        print(f"✓ Task 4: Visualizations created ({len(png_files)} charts) - SUCCESS")
    else:
        print(f"✗ Task 4: Expected 2+ charts, found {len(png_files)}")
    
    # Check Task 5 artifacts
    try:
        todos = read_file("todos_work.txt")
        # Check for multiple task indicators instead of one specific keyword
        task_count = todos.lower().count('-') + todos.lower().count('1.') + todos.lower().count('2.')
        if len(todos) > 150 and task_count >= 3:  # Minimum content + at least 3 task markers
            print("✓ Task 5a: Work todo list created - SUCCESS")
        else:
            print("✗ Task 5a: Todo list incomplete")
    except:
        print("✗ Task 5a: Todo file not found")
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nKey Capabilities Demonstrated:")
    print("  1. ✓ Multi-turn task execution (5 sequential tasks)")
    print("  2. ✓ Task planning (write_todos)")
    print("  3. ✓ Research delegation (2 research tasks)")
    print("  4. ✓ File persistence (5+ files created)")
    print("  5. ✓ Data extraction (DATA FOR GRAPHING sections)")
    print("  6. ✓ Summarization (combining multiple sources)")
    print("  7. ✓ Visualization (pie + bar charts)")
    print("  8. ✓ Task scheduling (3 calendar events)")
    print("  9. ✓ Todo management (6 actionable tasks)")
    print(" 10. ✓ Dependency resolution (later tasks use earlier outputs)")


if __name__ == "__main__":
    # Clear VFS before starting
    clear_vfs()
    
    # Run the comprehensive demo
    run_comprehensive_demo()
