#!/usr/bin/env python3
"""
Milestone 3 Week 5 Demo - Shows exactly what happens during sub-agent delegation
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from tools.delegation_tool import analyze_task_for_delegation, get_available_agents

def demonstrate_week5_workflow():
    """Demonstrate the exact workflow happening in Milestone 3 Week 5."""
    
    print("🎯 MILESTONE 3 WEEK 5: SUB-AGENT DELEGATION WORKFLOW")
    print("=" * 70)
    print("This shows EXACTLY what happens when a user makes a request...")
    print()
    
    # Initialize the system
    supervisor = SupervisorAgent()
    
    # Example user request
    user_request = "Research the latest trends in renewable energy and summarize the key findings"
    
    print(f"👤 USER REQUEST: {user_request}")
    print("\n🔄 STEP-BY-STEP WORKFLOW:")
    print("-" * 50)
    
    # STEP 1: Task Analysis
    print("\n1️⃣ TASK ANALYSIS")
    analysis = analyze_task_for_delegation(user_request)
    print(f"   📊 Analyzing task for delegation...")
    print(f"   🎯 Recommended Agent: {analysis['recommended_agent']}")
    print(f"   📈 Confidence Score: {analysis['confidence']:.2f}")
    print(f"   💭 Reasoning: {analysis['reasoning']}")
    
    # STEP 2: Agent Selection Decision
    print("\n2️⃣ AGENT SELECTION DECISION")
    should_delegate = analysis['confidence'] > 0.15  # Threshold check
    print(f"   🤔 Should delegate? {should_delegate}")
    print(f"   📏 Confidence threshold: 0.15")
    print(f"   ✅ Decision: {'DELEGATE' if should_delegate else 'HANDLE DIRECTLY'}")
    
    if should_delegate:
        # STEP 3: Sub-Agent Delegation
        print("\n3️⃣ SUB-AGENT DELEGATION")
        recommended_agent = analysis['recommended_agent']
        print(f"   🤖 Delegating to: {recommended_agent}")
        
        if recommended_agent == "SearchAgent":
            print("   🔍 SearchAgent will:")
            print("      - Conduct web research on renewable energy trends")
            print("      - Gather current market data and statistics")
            print("      - Analyze industry developments")
            print("      - Compile comprehensive research findings")
            
        elif recommended_agent == "SummarizerAgent":
            print("   📄 SummarizerAgent will:")
            print("      - Analyze provided content")
            print("      - Extract key points and themes")
            print("      - Create structured summary")
            print("      - Provide compression statistics")
    
    # STEP 4: Actual Execution
    print("\n4️⃣ ACTUAL EXECUTION")
    print("   ⚡ Running supervisor agent with delegation...")
    
    result = supervisor.run_with_context(user_request, [])
    
    print(f"   ✅ Success: {result['success']}")
    print(f"   🛠️ Tools Used: {result.get('tools_used', 0)}")
    
    if 'delegated_to' in result and result['delegated_to']:
        print(f"   🎯 Actually Delegated To: {result['delegated_to']}")
        print("   📋 Delegation successful!")
    else:
        print("   🏠 Handled directly by supervisor")
    
    # STEP 5: Response Analysis
    print("\n5️⃣ RESPONSE ANALYSIS")
    response = result.get('final_response', '')
    print(f"   📝 Response Length: {len(response)} characters")
    print(f"   🎨 Response Type: {'Delegated specialist output' if 'delegated' in response.lower() else 'Direct supervisor response'}")
    print(f"   📊 Quality: {'High (specialist expertise)' if 'delegated' in response.lower() else 'Standard (general knowledge)'}")
    
    print("\n" + "=" * 70)
    print("🎉 MILESTONE 3 WEEK 5 WORKFLOW COMPLETE!")
    print("=" * 70)
    
    return result

def show_available_specialists():
    """Show what specialist agents are available for delegation."""
    print("\n🤖 AVAILABLE SPECIALIST AGENTS")
    print("=" * 50)
    
    agents = get_available_agents()
    
    for i, agent in enumerate(agents, 1):
        print(f"\n{i}. **{agent['name']}** ({agent['type']})")
        print(f"   📋 Capabilities:")
        for cap in agent['capabilities']:
            print(f"      • {cap}")
        print(f"   🎯 Optimal For:")
        for opt in agent['optimal_for']:
            print(f"      • {opt}")

def demonstrate_different_task_types():
    """Show how different task types get routed to different agents."""
    print("\n🔀 TASK ROUTING EXAMPLES")
    print("=" * 50)
    
    test_tasks = [
        ("Summarize this 50-page research report", "SummarizerAgent"),
        ("Research current AI market trends", "SearchAgent"),
        ("What's 2+2?", "None (handled directly)"),
        ("Analyze the key points from this meeting", "SummarizerAgent"),
        ("Find the latest news about climate change", "SearchAgent")
    ]
    
    for task, expected in test_tasks:
        analysis = analyze_task_for_delegation(task)
        actual = analysis['recommended_agent'] or "None"
        
        status = "✅" if actual == expected.split()[0] else "⚠️"
        print(f"\n{status} Task: {task}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")
        print(f"   Confidence: {analysis['confidence']:.2f}")

def main():
    """Main demonstration of Milestone 3 Week 5."""
    print("🚀 UNDERSTANDING MILESTONE 3 WEEK 5")
    print("=" * 70)
    print("This demo shows the EXACT workflow that happens when:")
    print("• A user makes a request")
    print("• The system analyzes if it should delegate")
    print("• A specialist agent handles the task")
    print("• Results are returned to the user")
    print()
    
    # Show available specialists
    show_available_specialists()
    
    # Show task routing examples
    demonstrate_different_task_types()
    
    # Demonstrate the complete workflow
    result = demonstrate_week5_workflow()
    
    print(f"\n📋 FINAL RESULT PREVIEW:")
    print("-" * 30)
    print(result.get('final_response', '')[:300] + "...")

if __name__ == "__main__":
    main()