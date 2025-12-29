#!/usr/bin/env python3
"""
Test the specific scenario that was problematic
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def test_dinner_invitation_scenario():
    """Test the exact scenario that was giving bad responses."""
    print("🎯 TESTING DINNER INVITATION SCENARIO")
    print("=" * 50)
    
    supervisor = SupervisorAgent()
    conversation_history = []
    
    # Simulate the exact conversation flow
    messages = [
        "invite a friend to a party",
        "for a dinner ig", 
        "casual"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}️⃣ USER: {message}")
        
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': '2025-12-20T22:30:00'
        })
        
        # Get response
        result = supervisor.run_with_context(message, conversation_history)
        
        if result['success']:
            response = result['final_response']
            print(f"🤖 AGENT: {response[:300]}...")
            
            # Add agent response to history
            conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': '2025-12-20T22:30:00'
            })
            
            # Check if response is actually helpful
            is_actionable = any(keyword in response.lower() for keyword in [
                'template', 'example', 'here\'s', 'invitation', 'text', 'message'
            ])
            
            print(f"Quality: {'✅ ACTIONABLE' if is_actionable else '❌ VAGUE'}")
            
        else:
            print(f"❌ Error: {result.get('error')}")
            break

if __name__ == "__main__":
    test_dinner_invitation_scenario()