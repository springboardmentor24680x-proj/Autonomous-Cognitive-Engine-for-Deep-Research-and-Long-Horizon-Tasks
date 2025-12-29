#!/usr/bin/env python3
"""
Terminal Chat Interface for Autonomous Cognitive Engine
Test the agent directly in the terminal with conversation context
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from datetime import datetime

def main():
    """Run terminal chat interface."""
    print("🤖 Autonomous Cognitive Engine - Terminal Chat")
    print("=" * 50)
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("=" * 50)
    
    # Initialize agent and conversation history
    agent = SupervisorAgent()
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Check for clear command
            if user_input.lower() == 'clear':
                conversation_history = []
                print("\n🧹 Conversation history cleared!")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Add user message to history
            conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 20 messages (10 exchanges)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            # Show thinking indicator
            print("\n🤖 Assistant: ", end="", flush=True)
            print("thinking...", end="", flush=True)
            
            # Get agent response
            result = agent.run_with_context(user_input, conversation_history)
            
            # Clear thinking indicator
            print("\r🤖 Assistant: ", end="")
            
            if result['success']:
                response = result['final_response']
                print(response)
                
                # Add assistant response to history
                conversation_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Show tools used if any
                tools_used = result.get('tools_used', 0)
                if tools_used > 0:
                    print(f"\n🔧 Tools used: {tools_used}")
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Error: {error}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()