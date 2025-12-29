#!/usr/bin/env python3
"""
Simple Terminal Test for the Agent
Quick way to test conversation context and responses
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def test_conversation():
    """Test conversation with context."""
    print("🧪 Testing Agent Conversation Context")
    print("=" * 40)
    
    agent = SupervisorAgent()
    
    # Test 1: Simple question
    print("\n1️⃣ Testing simple question...")
    result1 = agent.run("What are good study tips?")
    print(f"✅ Success: {result1['success']}")
    print(f"📝 Response: {result1['final_response'][:100]}...")
    
    # Test 2: Follow-up question with context
    print("\n2️⃣ Testing follow-up question...")
    history = [
        {'role': 'user', 'content': 'What are good study tips?'},
        {'role': 'assistant', 'content': result1['final_response']}
    ]
    
    result2 = agent.run_with_context("What about time management?", history)
    print(f"✅ Success: {result2['success']}")
    print(f"📝 Response: {result2['final_response'][:100]}...")
    
    # Test 3: Chain question
    print("\n3️⃣ Testing chain question...")
    history.extend([
        {'role': 'user', 'content': 'What about time management?'},
        {'role': 'assistant', 'content': result2['final_response']}
    ])
    
    result3 = agent.run_with_context("Can you give me a daily schedule example?", history)
    print(f"✅ Success: {result3['success']}")
    print(f"📝 Response: {result3['final_response'][:100]}...")
    
    print("\n🎉 All tests completed!")

def interactive_chat():
    """Simple interactive chat."""
    print("\n💬 Interactive Chat Mode")
    print("Type 'quit' to exit")
    print("-" * 30)
    
    agent = SupervisorAgent()
    history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        # Add to history
        history.append({'role': 'user', 'content': user_input})
        
        # Get response
        result = agent.run_with_context(user_input, history)
        
        if result['success']:
            print(f"Bot: {result['final_response']}")
            history.append({'role': 'assistant', 'content': result['final_response']})
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Keep history manageable
        if len(history) > 10:
            history = history[-10:]

if __name__ == "__main__":
    print("🤖 Agent Terminal Tester")
    print("=" * 30)
    print("1. Run conversation tests")
    print("2. Interactive chat")
    
    choice = input("\nChoose (1 or 2): ").strip()
    
    if choice == "1":
        test_conversation()
    elif choice == "2":
        interactive_chat()
    else:
        print("Invalid choice. Running tests...")
        test_conversation()