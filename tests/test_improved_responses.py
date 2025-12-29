#!/usr/bin/env python3
"""
Test the improved response quality
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from datetime import datetime

def test_improved_responses():
    """Test that responses are now more helpful and actionable."""
    print("🧪 TESTING IMPROVED RESPONSE QUALITY")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    # Test scenarios that were problematic
    test_cases = [
        {
            "conversation": [
                {'role': 'user', 'content': 'write an essay on india'},
                {'role': 'assistant', 'content': 'India is a diverse country with rich culture...'}
            ],
            "request": "summarize that essay",
            "expected": "Should provide actual summary, not ask more questions"
        },
        {
            "conversation": [],
            "request": "invite a friend to a party",
            "expected": "Should provide actual invitation text/template"
        },
        {
            "conversation": [
                {'role': 'user', 'content': 'invite a friend to a party'},
                {'role': 'assistant', 'content': 'What kind of party?'}
            ],
            "request": "for a dinner",
            "expected": "Should provide dinner party invitation template"
        },
        {
            "conversation": [
                {'role': 'user', 'content': 'invite a friend to a party'},
                {'role': 'assistant', 'content': 'What kind of party?'},
                {'role': 'user', 'content': 'for a dinner'},
                {'role': 'assistant', 'content': 'What theme?'}
            ],
            "request": "casual",
            "expected": "Should provide casual dinner invitation template"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ TEST CASE {i}")
        print(f"Request: {test_case['request']}")
        print(f"Expected: {test_case['expected']}")
        print("-" * 40)
        
        result = supervisor.run_with_context(test_case['request'], test_case['conversation'])
        
        if result['success']:
            response = result['final_response']
            print(f"Response: {response[:200]}...")
            
            # Check if response is helpful
            is_helpful = (
                len(response) > 50 and  # Not too short
                not response.count('?') > 2 and  # Not too many questions
                ('template' in response.lower() or 
                 'example' in response.lower() or 
                 'here' in response.lower() or
                 len(response) > 100)  # Substantial content
            )
            
            print(f"Quality: {'✅ HELPFUL' if is_helpful else '❌ NEEDS IMPROVEMENT'}")
        else:
            print(f"❌ Failed: {result.get('error')}")

if __name__ == "__main__":
    test_improved_responses()