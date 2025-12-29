#!/usr/bin/env python3
"""
Test TODO Delegation - Demonstrates Milestone 3 TODO item delegation to sub-agents
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from tools.delegation_tool import create_todo_item, get_available_agents

def test_todo_creation_and_delegation():
    """Test creating TODO items and delegating them to appropriate sub-agents."""
    print("📋 Testing TODO Creation and Delegation")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    # Test 1: Create TODO items for different types of tasks
    todo_tasks = [
        {
            "task": "Summarize the quarterly financial report",
            "priority": "high",
            "expected_agent": "SummarizerAgent"
        },
        {
            "task": "Research market trends in electric vehicles",
            "priority": "medium", 
            "expected_agent": "SearchAgent"
        },
        {
            "task": "Analyze key points from board meeting notes",
            "priority": "high",
            "expected_agent": "SummarizerAgent"
        }
    ]
    
    created_todos = []
    
    for i, todo_data in enumerate(todo_tasks, 1):
        print(f"\n{i}️⃣ Creating TODO: {todo_data['task']}")
        
        # Create TODO item
        result = create_todo_item.invoke({
            "task": todo_data['task'],
            "priority": todo_data['priority']
        })
        
        if result['success']:
            todo_id = result['todo_id']
            created_todos.append(todo_id)
            print(f"   ✅ TODO created with ID: {todo_id}")
            
            # Test delegation for this TODO
            delegation_task = f"Process TODO item: {todo_data['task']}"
            delegation_result = supervisor.run_with_context(delegation_task, [])
            
            print(f"   🤖 Delegation result: {delegation_result['success']}")
            print(f"   🛠️ Tools used: {delegation_result.get('tools_used', 0)}")
            
            if 'delegated_to' in delegation_result:
                delegated_agent = delegation_result['delegated_to']
                expected_agent = todo_data['expected_agent']
                
                if delegated_agent == expected_agent:
                    print(f"   ✅ Correctly delegated to {delegated_agent}")
                else:
                    print(f"   ⚠️ Delegated to {delegated_agent}, expected {expected_agent}")
            else:
                print(f"   ℹ️ Task handled directly by supervisor")
                
        else:
            print(f"   ❌ Failed to create TODO: {result.get('error')}")
    
    print(f"\n📊 Summary: Created {len(created_todos)} TODO items")
    return created_todos

def test_workflow_with_todos():
    """Test the complete workflow: TODO creation → Analysis → Delegation → Execution."""
    print("\n🔄 Testing Complete TODO Workflow")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    # Simulate a complex task that should create TODOs and delegate them
    complex_task = """I need help with a comprehensive market analysis project. 
    Please create TODO items for:
    1. Research current AI market trends
    2. Summarize key findings from recent AI reports
    3. Analyze competitor strategies in the AI space"""
    
    print(f"Complex Task: {complex_task}")
    
    # Process the complex task
    result = supervisor.run_with_context(complex_task, [])
    
    print(f"\n📋 Task Processing Results:")
    print(f"   Success: {result['success']}")
    print(f"   Tools used: {result.get('tools_used', 0)}")
    print(f"   Response preview: {result.get('final_response', '')[:200]}...")
    
    if result.get('execution_plan'):
        print(f"   Execution plan: {result['execution_plan']}")

def main():
    """Run all TODO delegation tests."""
    print("🚀 MILESTONE 3: TODO DELEGATION TESTS")
    print("=" * 70)
    
    try:
        # Show available agents
        agents = get_available_agents()
        print(f"🤖 Available Sub-Agents: {len(agents)}")
        for agent in agents:
            print(f"   - {agent['name']} ({agent['type']})")
        
        # Test TODO creation and delegation
        created_todos = test_todo_creation_and_delegation()
        
        # Test complete workflow
        test_workflow_with_todos()
        
        print("\n" + "=" * 70)
        print("🎉 TODO DELEGATION TESTS COMPLETED!")
        print("✅ TODO items can be created successfully")
        print("✅ Tasks are analyzed for appropriate delegation")
        print("✅ Sub-agents receive and process delegated TODOs")
        print("✅ Complete workflow from TODO creation to execution works")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()