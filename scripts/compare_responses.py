#!/usr/bin/env python3
"""
Compare Terminal vs Web Agent Responses
"""

import sys
import os
import requests
import json
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def test_terminal_response():
    """Test terminal response."""
    print("🖥️ Testing Terminal Response...")
    agent = SupervisorAgent()
    
    query = "What are good study tips for college students?"
    result = agent.run_with_context(query, [])
    
    print(f"Success: {result['success']}")
    print(f"Length: {len(result.get('final_response', ''))}")
    print(f"Tools: {result.get('tools_used', 0)}")
    print("\nResponse:")
    print("=" * 60)
    print(result.get('final_response', ''))
    print("=" * 60)
    
    return result

def test_web_response():
    """Test web response via API."""
    print("\n🌐 Testing Web Response...")
    
    url = "http://localhost:8080/api/chat"
    data = {"message": "What are good study tips for college students?"}
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Length: {len(result.get('message', ''))}")
            print(f"Tools: {result.get('tools_used', 0)}")
            print("\nResponse:")
            print("=" * 60)
            print(result.get('message', ''))
            print("=" * 60)
            return result
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Comparing Terminal vs Web Agent Responses")
    print("=" * 50)
    
    terminal_result = test_terminal_response()
    web_result = test_web_response()
    
    if web_result:
        print("\n📊 COMPARISON:")
        print(f"Terminal length: {len(terminal_result.get('final_response', ''))}")
        print(f"Web length: {len(web_result.get('message', ''))}")
        print(f"Same content: {terminal_result.get('final_response', '') == web_result.get('message', '')}")
    else:
        print("\n❌ Could not get web response for comparison")