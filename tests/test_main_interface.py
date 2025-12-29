#!/usr/bin/env python3
"""
Test the main.py interface to see if the error is fixed
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from datetime import datetime

def test_main_interface_logic():
    """Test the exact logic used in main.py"""
    print("🧪 TESTING MAIN.PY INTERFACE LOGIC")
    print("=" * 50)
    
    # Initialize supervisor (same as main.py)
    supervisor = SupervisorAgent()
    conversation_history = []
    
    # Test the problematic request
    user_input = "plan a 5 days trip for 2 ppl to ooty"
    
    print(f"User Input: {user_input}")
    print("Processing...")
    
    try:
        # Add to conversation history (same as main.py)
        conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep history manageable (same as main.py)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        print("🔄 Processing with supervisor agent...")
        result = supervisor.run_with_context(user_input, conversation_history)
        
        # Add response to history (same as main.py)
        if result["success"]:
            conversation_history.append({
                'role': 'assistant',
                'content': result["final_response"],
                'timestamp': datetime.now().isoformat()
            })
        
        # Display results (same as main.py)
        print("\n" + "="*60)
        if result["success"]:
            print("✅ Task completed successfully!")
            print(f"🛠️ Tools used: {result.get('tools_used', 0)}")
            if result.get('execution_plan'):
                print(f"📋 Plan: {result['execution_plan']}")
            print("\n📝 Response:")
            print(result["final_response"])
        else:
            print("❌ Task failed:")
            print(result.get("error", "Unknown error"))
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_interface_logic()