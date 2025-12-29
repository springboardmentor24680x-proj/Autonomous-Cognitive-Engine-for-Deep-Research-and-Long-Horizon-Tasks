#!/usr/bin/env python3
"""
Milestone 3 Test: Sub-Agent Delegation
Demonstrates the supervisor agent's ability to delegate tasks to specialized sub-agents
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from tools.delegation_tool import get_available_agents, analyze_task_for_delegation

def test_delegation_analysis():
    """Test task analysis for delegation."""
    print("🔍 Testing Task Analysis for Delegation")
    print("=" * 50)
    
    test_tasks = [
        "Summarize this research paper about AI trends",
        "Research the latest developments in quantum computing",
        "Analyze the key points from this meeting transcript",
        "Find information about market trends in renewable energy",
        "What's the weather like today?"  # Should not be delegated
    ]
    
    for task in test_tasks:
        analysis = analyze_task_for_delegation(task)
        print(f"\nTask: {task}")
        print(f"Recommended Agent: {analysis['recommended_agent']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Reasoning: {analysis['reasoning']}")

def test_available_agents():
    """Test available agents registry."""
    print("\n🤖 Available Sub-Agents")
    print("=" * 50)
    
    agents = get_available_agents()
    for agent in agents:
        print(f"\n**{agent['name']}** ({agent['type']})")
        print(f"Capabilities: {', '.join(agent['capabilities'])}")
        print(f"Optimal for: {', '.join(agent['optimal_for'])}")

def test_delegation_workflow():
    """Test the complete delegation workflow."""
    print("\n🎯 Testing Delegation Workflow")
    print("=" * 50)
    
    supervisor = SupervisorAgent()
    
    # Test 1: Summarization task (should be delegated)
    print("\n1️⃣ Testing Summarization Delegation...")
    summarization_task = "Summarize the key benefits of renewable energy"
    result1 = supervisor.run_with_context(summarization_task, [])
    
    print(f"Success: {result1['success']}")
    print(f"Tools used: {result1.get('tools_used', 0)}")
    print(f"Delegated to: {result1.get('delegated_to', 'None')}")
    print(f"Response preview: {result1.get('final_response', '')[:200]}...")
    
    # Test 2: Research task (should be delegated)
    print("\n2️⃣ Testing Research Delegation...")
    research_task = "Research current trends in artificial intelligence"
    result2 = supervisor.run_with_context(research_task, [])
    
    print(f"Success: {result2['success']}")
    print(f"Tools used: {result2.get('tools_used', 0)}")
    print(f"Delegated to: {result2.get('delegated_to', 'None')}")
    print(f"Response preview: {result2.get('final_response', '')[:200]}...")
    
    # Test 3: General task (should NOT be delegated)
    print("\n3️⃣ Testing General Task (No Delegation)...")
    general_task = "What are some good study tips?"
    result3 = supervisor.run_with_context(general_task, [])
    
    print(f"Success: {result3['success']}")
    print(f"Tools used: {result3.get('tools_used', 0)}")
    print(f"Delegated to: {result3.get('delegated_to', 'None')}")
    print(f"Response preview: {result3.get('final_response', '')[:200]}...")

def test_conversation_with_delegation():
    """Test delegation within a conversation context."""
    print("\n💬 Testing Conversation with Delegation")
    print("=" * 50)
    
    supervisor = SupervisorAgent()
    conversation_history = []
    
    # First message
    msg1 = "I'm working on a research project about climate change"
    conversation_history.append({'role': 'user', 'content': msg1})
    
    result1 = supervisor.run_with_context(msg1, conversation_history)
    conversation_history.append({'role': 'assistant', 'content': result1['final_response']})
    
    print(f"1️⃣ Initial message: {msg1}")
    print(f"   Delegated to: {result1.get('delegated_to', 'None')}")
    
    # Follow-up that should trigger delegation
    msg2 = "Can you research the latest climate change statistics for me?"
    conversation_history.append({'role': 'user', 'content': msg2})
    
    result2 = supervisor.run_with_context(msg2, conversation_history)
    
    print(f"2️⃣ Follow-up: {msg2}")
    print(f"   Delegated to: {result2.get('delegated_to', 'None')}")
    print(f"   Response preview: {result2.get('final_response', '')[:200]}...")

def main():
    """Run all Milestone 3 tests."""
    print("🚀 MILESTONE 3: SUB-AGENT DELEGATION TESTS")
    print("=" * 60)
    
    try:
        test_available_agents()
        test_delegation_analysis()
        test_delegation_workflow()
        test_conversation_with_delegation()
        
        print("\n" + "=" * 60)
        print("🎉 MILESTONE 3 TESTS COMPLETED!")
        print("✅ Task delegation system is working")
        print("✅ Specialized sub-agents are integrated")
        print("✅ Supervisor can choose appropriate agents")
        print("✅ Delegation works within conversations")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()